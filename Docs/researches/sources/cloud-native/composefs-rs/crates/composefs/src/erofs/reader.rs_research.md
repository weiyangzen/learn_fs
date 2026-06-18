# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/reader.rs

## Purpose

`reader.rs` is the EROFS/composefs image parser, validator, object-reference scanner, and image-to-tree converter. It provides a zero-copy view over an image (`Image`), decodes compact and extended inode layouts through shared traits, walks directory data from block and inline storage, extracts composefs metacopy object IDs for repository garbage collection, and reconstructs a `tree::FileSystem<ObjectID>` from an EROFS image. It also contains a large regression and compatibility test suite covering Rust round trips, C `mkcomposefs`/`composefs-info` compatibility, malformed image rejection, whiteout behavior, and epoch-specific layout invariants.

## Important APIs, Types, and Functions

- `round_up(n, to)` is a low-level alignment helper used by both reader and writer code. It assumes `to` is a power-of-two style alignment.
- `InodeHeader` abstracts fields shared by `ExtendedInodeHeader`, `CompactInodeHeader`, references to `Inode<Header>`, and `InodeType`. It exposes layout, xattr count, mode, size, union field, link count, whiteout detection, xattr size, and extra trailing byte calculation.
- `XAttr`, `Inode<Header>`, and `InodeXAttrs` are `zerocopy` unsized structures over on-disk byte slices. Their methods decode xattr suffixes, values, padding, shared references, and local xattr iteration.
- `InodeOps` abstracts access to inode xattrs, inline payload, and raw block ranges. `raw_blocks` derives the range differently for `FlatPlain`, `FlatInline`, and `ChunkBased` layouts.
- `InodeType<'img>` is an enum wrapper around compact or extended inode references, avoiding dynamic dispatch while still allowing common trait calls.
- `Image<'i>` is the main parsed image view. Key methods include `open`, `open_max_size`, `restrict_to_composefs`, `inode`, `shared_xattr`, `image_slice`, `block`, `data_block`, `directory_block`, `root`, `inode_blocks`, `fsck_metadata`, `find_child_nid`.
- `DirectoryBlock`, `DirectoryEntry`, and `DirectoryEntries` decode EROFS directory entry headers and names. `n_entries` derives header count from the first entry's `name_offset`.
- `ErofsReaderError` is the typed error surface for malformed images, invalid inode IDs, bounds failures, directory hardlink/depth/self-reference issues, file-type mismatches, and duplicate names.
- `collect_objects<ObjectID>` opens a composefs-restricted image, runs metadata fsck, traverses reachable inodes, and returns the set of fsverity object IDs found in `trusted.overlay.metacopy`.
- `erofs_to_filesystem<ObjectID>` is the inverse of the writer: it parses the image, reconstructs a `tree::FileSystem`, validates directory and leaf nlink counts, handles hardlinks by repeated NID, reverses xattr escaping, and converts regular inline/external files, symlinks, devices, FIFOs, and sockets.

## Control Flow

Opening starts in `Image::open_max_size`: it rejects overly large inputs, parses the composefs header and EROFS superblock, computes block size from `blkszbits`, derives the inode and xattr region starts from superblock block addresses, and stores slices into the original image. `restrict_to_composefs` is an explicit second gate that checks composefs magic/version, supported `composefs_version` values 0/1/2, EROFS magic, required 4 KiB block size, supported feature bits, lack of compression/multidevice/fragments/custom xattr prefixes, `meta_blkaddr == 0`, and other composefs-only assumptions.

Inode lookup multiplies an EROFS NID by 32 bytes in the inode region, uses the low bit of the first format byte to choose compact versus extended headers, parses the fixed header with `zerocopy`, then parses enough variable-length bytes for xattrs and inline data by calling `additional_bytes`. Block access funnels through `image_slice` to centralize checked offset arithmetic. `inode_blocks` wraps raw block-range derivation with composefs-specific validation: non-chunk inodes cannot claim a size larger than the image, and any non-empty block range must fit within available image blocks.

`fsck_metadata` performs traversal-level validation by running `validate_v1_inline_layout` and `validate_epoch_invariants`. The V1 inline validator walks reachable inodes, finds FlatInline symlinks, and rejects layouts that would cross an inode block boundary in the pre-Linux-6.12 symlink fast path. Epoch validation treats `composefs_version` 0/1 as epoch 1 and version 2 as epoch 2. Epoch 1 requires exactly 256 lowercase hex root slots and disallows native whiteouts outside those stubs; epoch 2 rejects escaped V1 whiteout xattrs.

Directory iteration reads both block-based directory ranges and inline directory tails. `find_child_nid` checks inline entries first, then block entries. Higher-level tree reconstruction uses `dir_entries` to split `.` and `..` from normal children, `populate_directory` to recursively build directories, and `TreeBuilder` to track hardlinks, per-NID expected nlinks, and accumulated leaves. The recursion validates `.` and `..`, enforces a max depth derived from `PATH_MAX`, rejects duplicate names, validates directory nlinks as `2 + subdir_count`, and later compares leaf nlinks against the reconstructed filesystem's `nlinks()` result.

Object collection uses a work-set traversal (`BTreeSet` plus `HashSet`) from the root NID. For each directory it adds non-dot child NIDs. For every visited inode it scans shared and local xattrs, identifies `trusted.overlay.metacopy`, decodes `OverlayMetacopy<ObjectID>`, and records valid digests.

## State and Persistence Behavior

The reader itself is read-only over borrowed image bytes. `Image` stores borrowed slices and a `composefs_restricted` boolean that changes validation strictness. It does not persist data to disk. `collect_objects` builds transient visited sets and an object set. `erofs_to_filesystem` materializes a new in-memory `tree::FileSystem` with owned directory and leaf structures. Xattr transforms and inline file extraction allocate owned data only when converting to the tree representation.

The most important state transition is semantic, not persistent: calling `restrict_to_composefs` changes later behavior for `inode_blocks`, metacopy validation, and inline regular-file size enforcement. Callers that need composefs security and resource bounds must use the restricted path; the public high-level functions in this file do.

## Dependencies and Integration Points

- On-disk structs and constants come from `super::format`, including inode headers, `DataLayout`, file mode bits, composefs version constants, xattr prefixes, directory headers, and feature flags.
- `OverlayMetacopy` from `super::composefs` provides typed metacopy xattr decoding.
- `FsVerityHashValue` supplies digest parsing and algorithm metadata for object IDs.
- `tree` and `generic_tree::LeafId` provide the in-memory composefs filesystem model reconstructed by the reader.
- `MAX_INLINE_CONTENT` and `SYMLINK_MAX` enforce composefs limits during restricted conversion.
- `zerocopy` is central to safe-ish parsing of repr(C) on-disk data without manual byte copies; all range checking around it is critical.
- `repository.rs` uses `collect_objects` while traversing images for object reachability and fsck/GC-like behavior. Writer tests call reader paths to validate generated images.
- Optional external tools in tests include `fsck.erofs`, `mkcomposefs`, and `composefs-info`, guarded or detected where appropriate.

## Risks and Edge Cases

- This file is part of the untrusted image boundary. Arithmetic overflow and out-of-bounds slicing are the highest risks. The code consistently uses `checked_*`, `try_from`, `get`, and central `image_slice`, but future direct indexing would be risky.
- `round_up` uses bit math that is only correct for power-of-two alignments. Current call sites use EROFS slot/block/xattr alignments; new call sites should preserve that assumption.
- `Image::open` alone is permissive EROFS parsing; callers needing composefs invariants must call `restrict_to_composefs` and often `fsck_metadata`.
- Directory parsing derives entry count from the first header's `name_offset`; corrupted offsets can cause invalid images or truncated iteration. The iterator stops after the first entry error to avoid repeated failures.
- Inline directory handling must tolerate empty inline regions from C `mkcomposefs`; regression coverage exists because an older collector path panicked on this shape.
- Epoch whiteout handling is subtle: root hex stubs, user whiteouts, escaped V1 xattrs, and native V2 whiteouts have different semantics. This is an area where binary compatibility and semantic tree reconstruction can diverge.
- `extract_all_file_data` caps file size at image length before allocation and truncates after concatenating blocks and inline data. Restricted mode separately rejects oversized inline regular files, while chunk-based external files may legitimately report sizes much larger than the image.
- Recursive tree reconstruction uses a depth limit, but directory traversal for metadata fsck uses explicit stacks. Any added recursive validation should consider malicious depth.
- `calculate_min_mtime` behavior is indirectly tested in the reader test module even though the function lives in the writer; negative mtimes cast to `u64` have compatibility implications.

## Test Signals

The embedded tests provide strong behavioral coverage:

- Basic directory parsing: empty directories, inline entries, many entries, nested directories, mixed entry types, and child lookup.
- Object collection traversal, including a regression for C-generated empty inline directories.
- Round-trip conversion from dumpfile to EROFS and back for empty roots, inline files, symlinks, nested dirs, devices/FIFOs, xattrs, escaped overlay xattrs, external files, hardlinks, and mixed metadata.
- Restricted composefs validation rejects unsupported superblock features, compression, multidevice, extension slots, packed inodes, nonzero `meta_blkaddr`, and custom xattr prefixes.
- Corruption tests reject bad `.`/`..` entries, leaf nlink mismatches, directory nlink mismatches, duplicate dirents, oversized block ranges, hardlinked whiteouts, and malformed epoch invariants.
- Property tests round-trip random filesystems with SHA-256 and SHA-512 object IDs for V1 and V2.
- Compatibility tests compare V1 output byte-for-byte with C `mkcomposefs` for normal and unusual content, verify C `composefs-info` can read Rust-generated V1/V2 images, and normalize known C reader limitations.
- Layout regression tests cover V1 symlink block-boundary padding and a fault-injected validator path that catches the bad layout.

## Research Notes

This file is the validation counterpart to `erofs/writer.rs`. The strongest integration contract is that writer-generated images must pass `Image::open(...).restrict_to_composefs()`, `fsck_metadata`, `collect_objects`, and `erofs_to_filesystem`; the reader also intentionally accepts some C-generated image variants. Any change to xattr prefixing, whiteout encoding, inode traversal ordering, directory layout, or epoch versioning must be checked against both Rust round-trip tests and C compatibility tests.
