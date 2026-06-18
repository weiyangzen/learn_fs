# sources/distributed-fs/ceph-client/io_uring/sync.c

Purpose: implements file synchronization and space allocation opcodes: `sync_file_range`, `fsync`, and `fallocate`.

Important APIs/types/functions: `struct io_sync` stores file, offset, length, flags, and fallocate mode. Entry points are `io_sfr_prep()`, `io_sync_file_range()`, `io_fsync_prep()`, `io_fsync()`, `io_fallocate_prep()`, and `io_fallocate()`.

Control flow: prep validates unused SQE fields, stores offsets/length/flags, validates fsync datasync flags and nonnegative fsync offset, and forces async. Issue asserts blocking context, calls `sync_file_range()`, `vfs_fsync_range()`, or `vfs_fallocate()`, and posts the result. Fallocate emits modify notification on success.

State and persistence: request state is transient, but operations persist filesystem sync/allocation effects and may update filesystem metadata.

Dependencies/integration: depends on VFS sync/allocation helpers, fsnotify for fallocate, and io_uring async issue semantics.

Risks/test signals: risks are overflow in `off + len` end handling, invalid flag acceptance, and blocking operations accidentally issued nonblocking. Test datasync/full fsync, `len == 0` end-to-LLONG_MAX behavior, sync range flags, fallocate modes, negative offsets, and nonblocking warnings.
