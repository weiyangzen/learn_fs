<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/writablesuite.go -->
# sources/distributed-fs/ipfs-kubo/fuse/fusetest/writablesuite.go

## Purpose

This file defines the shared behavioral conformance suite for writable Kubo FUSE mounts. It is used by both `/mfs` and writable `/ipns/local` to ensure the shared `fuse/writable` adapter behaves like a practical POSIX filesystem.

## Important APIs, Types, and Functions

`MountFunc` abstracts mount creation from a `writable.Config`. `RunWritableSuite` registers subtests for reads, writes, append, multiwrite, directory creation, immediate create/mkdir attrs, renames, removals, fsync, truncate, large files, temporary-file replacement patterns, sparse writes, `O_EXCL`, symlinks, metadata persistence, xattrs, concurrent writes/reads, read/write snapshots, and filesystem thrash. Helpers include `RandBytes`, `WriteFile`, `WriteFileOrFail`, `VerifyFile`, `CheckExists`, and `Lchtimes`.

## Control Flow, State, and Integration

Each subtest calls the supplied mount function to create a fresh filesystem. Data is persisted through the mount's backing MFS/IPNS state, then checked through normal `os`, `syscall`, and `unix` calls. Some tests enable `StoreMtime` or `StoreMode` to exercise UnixFS optional metadata. Concurrent tests use goroutines and `sync.WaitGroup`; race builds reduce workload size.

## Dependencies, Risks, and Test Signals

The suite depends on standard filesystem syscalls, `golang.org/x/sys/unix`, `testify/require`, and `fuse/writable`. It guards high-risk areas: MFS descriptor locks, kernel attr caching after create, non-atomic rename behavior, sparse write visibility, symlink metadata, xattr error mapping, fsync cache invalidation, and large-file readahead concurrency. Failures usually point to regressions in `writable.go`, mount capabilities, or mutable cache handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/writablesuite.go -->
