# sources/distributed-fs/ceph-client/io_uring/sync.h

Purpose: declares sync-related io_uring operation hooks.

Important APIs/types/functions: prototypes cover `io_sfr_prep()`, `io_sync_file_range()`, `io_fsync_prep()`, `io_fsync()`, `io_fallocate_prep()`, and `io_fallocate()`.

Control flow: none.

State and persistence: none.

Dependencies/integration: consumed by opcode dispatch for sync, fsync, and fallocate.

Risks/test signals: compile integration and filesystem operation tests validate this header.
