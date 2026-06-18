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
