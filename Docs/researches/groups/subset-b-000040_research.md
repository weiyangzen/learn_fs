# subset-b-000040 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/reader.rs -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/writer.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/writer.rs

## Purpose

`writer.rs` serializes a validated `tree::FileSystem<ObjectID>` into a composefs-compatible EROFS image. It supports three format versions: V0 and V1 for C `mkcomposefs` compatibility, and V2 as the Rust-native format. The writer is intentionally two-pass: the first pass records inode, xattr, block, and final offsets without emitting bytes, and the second pass serializes using those resolved offsets. This is necessary because EROFS NIDs and xattr references depend on final byte positions.

## Important APIs, Types, and Functions

- `ValidatedFileSystem<ObjectID>` wraps `tree::FileSystem<ObjectID>` and can only be built with `ValidatedFileSystem::new`, which runs `validate_filesystem`.
- `validate_filesystem` runs `fs.fsck()` and enforces the EROFS-specific invariant that whiteout inodes, represented as character devices with `rdev == 0`, cannot have `nlink > 1`.
- `mkfs_erofs` writes an image using the default `FormatVersion` and requires a `ValidatedFileSystem`.
- `mkfs_erofs_versioned` writes an image for an explicit format version.
- `mkfs_erofs_inner` is the internal entry point used by high-level filesystem operations. It mutates the tree for epoch 1 by adding overlay whiteout stubs, prepares inodes, runs first and second passes, and returns image bytes.
- `WriterFaults` and `mkfs_erofs_with_faults` are test-only hooks for deterministic layout fault injection.
- `WriteContext` carries format version, min mtime, header flags, composefs header version, and optional test faults through a write pass.
- `Output` abstracts first-pass counting and second-pass byte emission. It owns the methods that write typed headers, pad, compute NIDs, compute shared xattr references, and expose recorded offsets.
- `FirstPass`, `SecondPass`, and `Layout` implement the two-pass output model.
- Internal model types include `XAttr`, `InodeXAttrs`, `InodeRef`, `DirEnt`, `InodeMeta`, `Directory`, `Leaf`, `InodeContent`, and `Inode`.
- `InodeCollector` turns the tree into an ordered inode vector. It uses BFS for epoch 1 compatibility and DFS for epoch 2.
- `share_xattrs` promotes duplicated xattrs into the shared xattr table with epoch-specific ordering rules.
- `prepare_erofs_inodes` collects inodes, adds root opaque xattrs for epoch 1, computes header flags, chooses composefs version fields, shares xattrs, and calculates the minimum mtime.
- `write_erofs` emits the composefs header, superblock, inode table, shared xattrs, and directory data blocks.

## Control Flow

The safe public path is `ValidatedFileSystem::new(fs)` followed by `mkfs_erofs` or `mkfs_erofs_versioned`. Validation first calls `fs.fsck()` and then scans leaves for hardlinked whiteouts. Once inside `mkfs_erofs_inner`, epoch 1 formats call `fs.add_overlay_whiteouts()` before collecting inodes, so missing root stub entries are synthesized before serialization.

Inode preparation starts with `InodeCollector::collect`. Epoch 2 uses recursive DFS via `collect_dir`, reserving a directory inode before children and then filling its content after children have been collected. Epoch 1 uses `collect_tree`, a queue-based BFS matching C `mkcomposefs`. It first computes canonical directories for hardlinked leaves using a DFS pre-pass because C dumpfile order determines the "original" hardlink target. During BFS, noncanonical hardlinks may be represented as `InodeRef::Deferred` until the canonical inode has been assigned. A post-BFS pass resolves deferred references and corrects dirent file types.

Epoch 1 whiteout behavior is compatibility-heavy. `add_overlay_whiteouts` creates root stubs outside this file, while `collect_tree` escapes user-provided `CharacterDevice(0)` leaves into regular files with overlay whiteout xattrs, skipping internally generated root stubs by checking root location, two-hex names, file metadata, and SELinux xattr inheritance. Parent directories that contain escaped whiteouts get overlay whiteouts/opaque marker xattrs. V0 auto-bumps `composefs_version` from 0 to 1 if user whiteouts were escaped; V1 always writes 1; V2 writes 2.

After collection, `prepare_erofs_inodes` adds the epoch 1 root opaque xattr, computes ACL header flags from POSIX ACL xattrs, calls `share_xattrs`, and calculates `min_mtime`. `share_xattrs` sorts V1 locals by full xattr key to match C behavior, writes V1 shared xattrs in descending full-key order with inodes-end-relative references, and uses natural `BTreeMap` order with absolute word offsets for V2.

Serialization happens in `write_erofs`. The first pass uses `FirstPass` to count bytes and record offsets. In this pass, references that depend on final offsets return placeholder zeroes, but the control flow and padding choices must be identical to the second pass. The second pass receives the recorded `Layout` and writes actual bytes while resolving NIDs, xattr refs, block starts, xattr block address, root NID, and final block count. Test faults record decisions in the first pass and replay them in the second pass so intentionally malformed images remain structurally coherent enough for validator tests.

Each inode is serialized by `Inode::write_inode`. It computes metadata from directory or leaf content, chooses compact inodes for epoch 1 only when mtime, nlink, UID, GID, and size fit compact constraints, otherwise writes extended headers. Epoch 2 always uses extended inodes and zeroes `mtime_nsec`. FlatInline payloads run epoch-specific padding: V1 aligns symlink inode starts away from old-kernel EUCLEAN cases and pads non-symlink inline tails like C; V2 uses the origin/main block-boundary algorithm. The inode then writes xattrs, inline directory/file/symlink/chunk marker bytes, and slot padding. After all inodes, the writer pads the inode table, writes shared xattrs, pads to block boundary, and writes directory blocks.

## State and Persistence Behavior

The writer is deterministic for a given tree and format version, except that `mkfs_erofs_inner` mutates the input tree for epoch 1 by adding overlay whiteout stubs. Public APIs therefore take `&mut` filesystem wrappers. The emitted image is returned as `Box<[u8]>`; persistence to a repository is handled by `filesystem_ops.rs` and `repository.rs`.

`FirstPass` stores only layout state and byte counts. `SecondPass` stores the final byte vector. `WriteContext` is constant across a write call, but test-only `WriterFaults` changes from decision-recording to replay mode between passes. `InodeCollector` holds transient inode vectors, hardlink maps, nlink maps, and references into the source tree.

The writer encodes persistence-critical format choices: epoch 1 versus epoch 2 inode ordering, compact versus extended inode headers, root/stub whiteout behavior, xattr sharing order, mtime storage, chunk format computation, superblock `build_time`, header flags, and `composefs_version`. These choices determine fsverity digests and repository object identities.

## Dependencies and Integration Points

- Depends on `erofs::format` for all on-disk structs, constants, `FormatVersion`, `FormatEpoch`, file types, layouts, feature flags, and xattr names.
- Uses `reader::round_up` for alignment, linking writer layout assumptions to reader helper behavior.
- Uses `OverlayMetacopy` to encode external regular-file object digests in `trusted.overlay.metacopy`, plus redirect xattrs derived from object pathnames.
- Uses `FsVerityHashValue` and `LeafId` from the generic tree model.
- Accepts `tree::FileSystem`, `tree::Directory`, `tree::LeafContent`, and `tree::RegularFile` as the source model.
- High-level APIs in `filesystem_ops.rs` call `validate_filesystem` and `mkfs_erofs_inner` when committing or computing image IDs.
- Reader tests validate writer output extensively, including C compatibility. The writer's own local test module only directly tests `compute_chunk_format`, so most writer regression signals live in `reader.rs`.

## Risks and Edge Cases

- Output digest stability depends on traversal order, xattr sorting, padding, and timestamp logic. Small changes can break repository identity or C binary compatibility.
- Epoch 1 mutates the input tree by adding overlay whiteout stubs. Callers that reuse the same filesystem across versions must understand this side effect; `filesystem_ops::commit_images` validates once, then writes configured versions in order.
- The two-pass design assumes both passes execute exactly the same structural decisions. Any branch depending on actual offset resolution, random state, or non-replayed faults can make second-pass offsets diverge. Debug assertions catch some divergence at inode-table end and final end.
- `round_up` alignment and `output.pad` are core to inode slot, xattr word, and block alignment. Wrong alignment can corrupt NIDs, xattr references, or old-kernel symlink behavior.
- Device numbers are converted to `u32` with `expect`, symlink lengths assert against `SYMLINK_MAX`, and some size conversions assume valid prechecked data. `ValidatedFileSystem` reduces but does not eliminate the need for cautious new call sites.
- Epoch 1 hardlink canonicalization is subtle because it emulates C's DFS-original plus BFS-emission behavior. Simplifying it to first-BFS occurrence would break binary compatibility.
- Whiteout escaping and root stub detection rely on exact metadata matching. Changes to `add_overlay_whiteouts`, root xattr inheritance, or mode defaults must be reflected here.
- `calculate_min_mtime` casts signed seconds to `u64`; current tests document behavior with negative mtimes. Any change can alter V1 `build_time`.
- Chunk-based external file encoding differs by epoch: V1 computes a size-sensitive chunk format, while V2 hardcodes 31. This impacts readers and compatibility.

## Test Signals

Direct tests in this file cover `compute_chunk_format` boundary values. Most coverage is in `reader.rs` because reader tests generate images through this writer:

- Round-trip tests across inline files, symlinks, directories, devices, xattrs, external files, hardlinks, mixed types, and random proptest filesystem specs.
- V1 and V2 property tests with SHA-256 and SHA-512 object IDs.
- C compatibility checks using `mkcomposefs`, `composefs-info`, debug dumps, and binary identity comparisons for V1.
- Regression tests for empty inline directories, multi-block directories, duplicate dirents, V1 symlink block-boundary padding, negative mtimes, and hardlinked whiteout rejection.
- Epoch invariant tests confirm V1 root stubs and V2 no-escaped-whiteout rules.
- Fault-injection tests validate that the reader catches intentionally skipped V1 symlink padding.

## Research Notes

This file is the digest-defining serialization core for composefs-rs. The main behavioral contracts are: validated filesystems must not trigger writer panics; V1/V0 output must preserve C `mkcomposefs` compatibility; V2 output must remain stable as the Rust-native format; and all writer output must be accepted by `reader.rs` validation and reconstruction. Changes should be paired with digest/compatibility tests, not only structural parser tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/erofs/writer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/filesystem_ops.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/filesystem_ops.rs

## Purpose

`filesystem_ops.rs` adds high-level convenience operations directly to `FileSystem<ObjectID>`. It bridges the in-memory composefs tree with repository storage, EROFS image generation, fsverity digest computation, and dumpfile printing. The module is intentionally small: it delegates validation and serialization to `erofs::writer`, digesting to `fsverity`, repository persistence to `Repository`, and textual output to `dumpfile`.

## Important APIs, Types, and Functions

- `FileSystem<ObjectID>::commit_images(&mut self, repository, image_name)` validates the filesystem once, writes an EROFS image for every format version configured in the repository, stores each image, and returns a `HashMap<FormatVersion, ObjectID>` mapping each version to the stored image digest.
- `FileSystem<ObjectID>::commit_image(&mut self, repository, image_name)` is the single-default-version convenience wrapper. It calls `commit_images`, then removes and returns the digest for `repository.format_config().default`.
- `FileSystem<ObjectID>::compute_image_id(&mut self, version)` serializes the filesystem to an EROFS image for the supplied `FormatVersion` and returns the fsverity digest without writing it to a repository.
- `FileSystem<ObjectID>::print_dumpfile(&self)` writes the filesystem to stdout in composefs dumpfile format.

## Control Flow

`commit_images` is the primary persistence flow. It first calls `validate_filesystem(self)` so all configured image versions share the same initial validation gate. It reads the repository's `FormatConfig`, initializes an output map, then iterates `formats.versions()`. The first version in that iteration is treated as the default/primary version and receives the optional named ref (`image_name`); subsequent extra versions are written anonymously with `None`. Each loop calls `mkfs_erofs_inner(self, version, None)` to generate bytes, then `repository.write_image(name, &image_data)` to persist the image and obtain its digest. The digest is inserted into the result map by format version.

`commit_image` reads the configured default version, delegates to `commit_images`, and extracts that version's digest from the returned map. The `expect("format version must be in map")` is justified by using the same repository format config for both the default lookup and the `versions()` iteration.

`compute_image_id` directly calls `mkfs_erofs_inner` and then `compute_verity` over the generated bytes. Unlike `commit_images`, it does not validate internally; the comment states callers are responsible for ensuring validity. This keeps it cheaper but makes it a sharper API.

`print_dumpfile` just calls `write_dumpfile(&mut stdout(), self)` under an error context.

## State and Persistence Behavior

All EROFS-producing methods take `&mut self` because `mkfs_erofs_inner` can mutate the filesystem for epoch 1 by adding overlay whiteout stubs. `commit_images` persists images into the supplied `Repository` and may update a named ref for the default format only. Extra configured versions are stored as image objects but not assigned the named ref. The method returns only digest mappings; repository side effects are performed by `Repository::write_image`.

`compute_image_id` does not persist anything, but it still mutates through the writer path for epoch 1 formats. `print_dumpfile` is read-only with respect to the filesystem and writes to process stdout.

## Dependencies and Integration Points

- `dumpfile::write_dumpfile` is the text serialization endpoint for `print_dumpfile`.
- `erofs::writer::{mkfs_erofs_inner, validate_filesystem}` provides image generation and validation.
- `erofs::format::FormatVersion` is used as the key for multi-format image results.
- `fsverity::compute_verity` and `FsVerityHashValue` define digest computation and the object ID type.
- `repository::Repository` supplies format configuration and durable image writes.
- `tree::FileSystem` is extended by this module via an inherent impl.
- `repository.rs` tests and callers use `commit_image`, `commit_images`, and `compute_image_id` to store images and refs.

## Risks and Edge Cases

- `commit_images` validates only once before writing all versions. Since epoch 1 writing can mutate the filesystem by adding whiteout stubs, version order in `FormatConfig::versions()` matters for side effects and named-ref semantics. The implementation explicitly gives the named ref to the first/default version.
- `compute_image_id` skips validation. If called on a malformed tree, it can hit writer assertions or produce invalid output. Existing comments rely on callers using freshly built valid trees.
- `commit_image` assumes the default format is present in the versions iterator. If `FormatConfig` ever allowed an inconsistent default/extras set, the `expect` would panic.
- Multi-format commits can produce different digests for V1 and V2 because on-disk layouts differ. Callers must keep the `FormatVersion` key with the digest instead of treating all image IDs as interchangeable.
- Because writer calls mutate `self`, repeated calls to `commit_images`, `commit_image`, or `compute_image_id` on the same filesystem can observe a filesystem already modified by prior epoch 1 image generation.
- `print_dumpfile` writes directly to stdout, which is useful for CLI plumbing but less flexible for library callers that need an arbitrary writer.

## Test Signals

This file has no local test module. Relevant tests are integration-style tests elsewhere:

- `repository.rs` contains callers and tests for committing images and refs, including dual-format behavior such as `test_commit_images_both_named_ref_points_to_v1`.
- `reader.rs` tests exercise `mkfs_erofs_inner` outputs that these high-level methods rely on, including validation, round trips, C compatibility, and format-version differences.
- Repository fsck/GC paths call reader object collection over images written through these flows, so failures in persistence shape would surface in repository tests.

## Research Notes

This module is the ergonomic boundary most repository-facing code should use. Its most important contract is that repository configuration decides which EROFS formats are written and which one receives the named ref. Code that only needs a digest can use `compute_image_id`, but should validate first or use the commit path if repository persistence is desired.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/filesystem_ops.rs -->
