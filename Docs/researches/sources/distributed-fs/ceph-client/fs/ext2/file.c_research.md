# sources/distributed-fs/ceph-client/fs/ext2/file.c

Purpose: Provides ext2 regular-file operations for buffered I/O, direct I/O, DAX I/O/faults, mmap setup, fsync, open/release, and inode operation hooks.

Important APIs/types/functions: Exports `ext2_file_operations`, `ext2_file_inode_operations`, and `ext2_fsync`. Key helpers are `ext2_file_read_iter`, `ext2_file_write_iter`, `ext2_dio_read_iter`, `ext2_dio_write_iter`, `ext2_dio_write_end_io`, DAX `ext2_dax_read_iter`, `ext2_dax_write_iter`, `ext2_dax_fault`, `ext2_file_mmap_prepare`, `ext2_release_file`, and `ext2_file_open`.

Control flow: Reads route to DAX, direct I/O, or generic buffered I/O. Writes route similarly; direct writes take the inode lock, run generic write checks and metadata updates, force synchronous DIO for extending or unaligned writes, and fall back to buffered writes on `-ENOTBLK` or remaining iterator data. DAX writes use `dax_iomap_rw` and update i_size after successful extension. Release of writable files discards reservation windows under `truncate_mutex`.

State and persistence behavior: Fsync uses `mmb_fsync` for metadata buffer tracking and reports metadata I/O errors through `ext2_error`. Direct/DAX write completion updates `i_size` and marks inodes dirty for extending writes. Open enables `FMODE_CAN_ODIRECT` and initializes quotas. Release drops in-memory reservation windows, not disk data.

Dependencies and integration points: Depends on `ext2_iomap_ops`, `ext2_aops`, quota, iomap DIO, DAX, generic file helpers, VFS fileattr/xattr/ACL hooks, tracepoints, leases, splice, and THP unmapped-area selection.

Risks: Direct I/O to holes is intentionally forced to buffered fallback to avoid stale data exposure in non-extent mappings. DAX fault lock ordering is documented and must stay consistent with truncate and freeze. Partial direct writes require page-cache invalidation and writeback ordering. Reservation discard on release affects allocation locality but not correctness.

Test signals: Buffered/direct/DAX read-write matrices; unaligned DIO fallback; extending DIO i_size updates; fsync metadata error injection; mmap page faults with DAX; writable close discards reservation; quota open behavior.
