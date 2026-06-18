# sources/distributed-fs/ceph-client/fs/fuse/passthrough.c

## Purpose
Implements FUSE passthrough operations that satisfy read, write, splice, and mmap through a kernel backing file while keeping FUSE inode metadata coherent.

## Important APIs, Types, And Functions
`fuse_passthrough_read_iter()`, `fuse_passthrough_write_iter()`, `fuse_passthrough_splice_read()`, `fuse_passthrough_splice_write()`, and `fuse_passthrough_mmap()` wrap `backing_file_*` helpers using `struct backing_file_ctx`. `fuse_file_accessed()` invalidates FUSE atime after backing reads. `fuse_passthrough_end_write()` updates FUSE write attributes. `fuse_passthrough_open()` resolves a server-supplied backing ID, opens a per-FUSE-file backing handle, and stores backing credentials. `fuse_passthrough_release()` drops the file and credential references.

## Control Flow
Read and splice-read operations short-circuit zero length and otherwise dispatch to backing-file helpers with access callbacks. Write and splice-write take the FUSE inode lock around backing writes so size and write metadata updates remain serialized. `mmap` delegates to `backing_file_mmap()`. Open validates a positive `backing_id`, looks up the shared `fuse_backing`, opens a per-file backing view at the FUSE path, stores it in `ff`, and returns the backing object for inode-mode ownership.

## State And Persistence
Per-open state is `ff->passthrough` and `ff->cred`. Persistent data is written by the lower backing file. FUSE metadata is adjusted through atime invalidation and write attribute updates so cached inode state reflects lower-file operations.

## Dependencies And Integration Points
Depends on `linux/backing-file.h`, FUSE backing lookup/refcounting, and iomode code that decides when passthrough can be enabled. Integrates with the FUSE file operations table for passthrough-capable files and with `fuse_file_io_open()`/release.

## Risks
Credential handling is security-sensitive because lower-file access runs under backing credentials. Writes must keep FUSE inode size/ctime/mtime coherent with lower writes. Open failure paths must release both `fuse_backing` and per-file backing handles. Passthrough mmap can bypass ordinary FUSE page-cache semantics, so it relies on iomode exclusion.

## Test Signals
Validate reads, writes, splice I/O, mmap faults, credential-denied backing opens, zero-length I/O, size and timestamp updates after writes, atime invalidation after reads, and cleanup after failed passthrough open.
