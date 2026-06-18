# sources/cloud-native/composefs-rs/crates/composefs/src/fs.rs

## Purpose
This module is the main bridge between live Linux filesystem trees and composefs in-memory trees. It can scan a directory into `FileSystem<ObjectID>`, store or compute fs-verity digests for external file content, apply container-specific xattr filtering and OCI transformations, and write a composefs tree back to a directory. It also defines the `ObjectStore` abstraction and the C-compatible `FlatDigestStore`.

## Important APIs, Types, and Functions
`ObjectStore<ObjectID>` abstracts `ensure_object_from_fd()` and `write_semaphore()` so filesystem reading can target either `Repository<ObjectID>` or other object layouts. `FlatDigestStore` implements a flat `<store>/xx/rest-of-digest` layout compatible with C `mkcomposefs --digest-store`. `write_to_path()` recursively materializes a `FileSystem` into a target directory using `write_directory_contents()`, `write_directory()`, `write_leaf()`, and `set_file_contents()`.

The scan path uses `FilesystemScanner`, `FileDevIno`, `PendingFile`, and `ChannelHandler`. `PendingFile::Inline` holds small content at or below `INLINE_CONTENT_MAX_V0`; `PendingFile::External` records `(dev, ino)` and size for later fs-verity resolution. `HardlinkBehavior` controls whether shared source inodes are deduplicated into shared `LeafId`s or broken into independent leaves. `ReadFilesystemOpts` exposes a custom object store, semaphore, and hardlink mode. Public readers are `read_filesystem()`, `read_filesystem_with_opts()`, `read_filesystem_filtered()`, `read_container_root()`, and `read_file()`.

## Control Flow
Writing walks the root directory, creates directories and special files with `rustix`, writes inline data through `O_TMPFILE` when supported, and copies external object content out of the repository. Reading starts a blocking scanner task and an async stream of large-file work items. The scanner opens each inode with `NOFOLLOW`, reads stat and xattrs, recurses into directories, reads small regular files inline, captures symlinks and device metadata, and sends large regular file descriptors through a bounded Tokio channel. The async side gates work with a semaphore, spawns blocking digest/store tasks, collects `TaskResult::Verity` results by `FileDevIno`, waits for the scan result, then maps `PendingFile` to final `RegularFile<ObjectID>`.

`FlatDigestStore::ensure_object_from_fd()` copies the input fd into an anonymous tmpfile, reopens it read-only, enables fs-verity when possible, measures the kernel digest or computes a userspace fallback when `insecure` allows it, creates the digest prefix directory, and atomically links the tmpfile into its final content-addressed path. Duplicate objects are accepted via `EEXIST`.

## State and Persistence Behavior
The scanner keeps transient in-memory state: a hardlink map and leaf vector. Persistent side effects occur when an object store is supplied: repositories or flat digest stores receive content-addressed files, and `write_to_path()` creates files, directories, symlinks, and device nodes in the output tree. `FlatDigestStore` uses anonymous tmpfiles plus `linkat` for atomic publication and avoids in-memory buffering for object copies. Xattrs are read into `BTreeMap`s; `read_container_root()` filters to the container allowlist and then calls OCI tree transforms.

## Dependencies and Integration Points
This file integrates `rustix` fd-based filesystem operations, Tokio `Semaphore`, `JoinSet`, and streams, `Repository`, `generic_tree`, `tree`, `fsverity`, and utility helpers such as `proc_self_fd()` and `reopen_tmpfile_ro()`. It relies on `FsVerityHashValue` and `FsVerityHasher` for generic hash support. It feeds composefs image generation through `FileSystem<ObjectID>` and supports C compatibility through `FlatDigestStore`.

## Risks and Edge Cases
The write path for external files reads the entire object into memory, and the comment notes this should become streaming or reflink-aware. Small-file reading calls `read()` once into spare capacity, so short reads on regular files are a risk unless upstream assumptions hold. `read_xattrs()` uses fixed 64 KiB buffers, so unusually large xattr lists or values may fail. The async scanner can silently ignore channel send failures after cancellation, which is acceptable for early error paths but makes root-cause context depend on the async side. `FlatDigestStore` has an `insecure` fallback that computes userspace hashes without kernel immutability guarantees. Hardlink mode changes image semantics and compatibility.

## Test Signals
Unit tests cover `set_file_contents()` and flat digest store layout, content preservation, and idempotent duplicate storage. Broader behavior is indirectly covered by tests in `generic_tree`, `fsverity`, repository, and image generation paths. Useful additional tests would exercise partial reads, xattr buffer overflow behavior, hardlink `Tracked` versus `Break`, cancellation while scanning, and write-back of external large files without allocating the full file.
