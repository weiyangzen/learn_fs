# sources/distributed-fs/ceph-client/fs/udf/dir.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/dir.c` implements UDF directory file operations, primarily `readdir`/`iterate_shared`, plus directory open/release/seek state handling. The source was read as a complete 162-line implementation.

## Important APIs, Types, and Functions

The main function is `udf_readdir`. Supporting functions are `udf_dir_open`, `udf_dir_release`, and `udf_dir_llseek`. The exported operation table is `udf_dir_operations`, which wires `.read`, `.iterate_shared`, `.unlocked_ioctl`, `.fsync`, `.llseek`, `.open`, `.release`, and `.setlease`.

## Control Flow

`udf_readdir` emits `.` at position zero, converts the VFS cookie to a byte offset by shifting `(ctx->pos - 1) << 2`, and stops once the offset reaches directory size. If the directory version changed since the last read or a seek happened, it rescans from the beginning until the requested byte offset to avoid starting in the middle of a variable-length file identifier. It initializes `udf_fileident_iter`, skips deleted or hidden entries unless mount flags request them, emits `..` for parent FIDs, converts UDF names through `udf_get_filename`, maps the target ICB to a physical inode number with `udf_get_lb_pblock`, and calls `dir_emit`.

## State and Persistence Behavior

The file stores a `u64` directory i_version snapshot in `file->private_data` on open. It updates that snapshot after a valid iteration position is established. No persistent directory entries are changed here; mutation and CRC rewriting live in `directory.c` and namei paths.

## Dependencies and Integration Points

The implementation depends on `udf_fileident_iter` helpers from `directory.c`, UDF filename conversion, mount flags `UDF_FLAG_UNDELETE` and `UDF_FLAG_UNHIDE`, VFS directory emit helpers, inode versioning, generic directory read/seek helpers, UDF ioctl, UDF fsync, and generic leases.

## Risks and Edge Cases

Directory offsets are synthetic cookies in four-byte units; invalid or stale positions require a full rescan because UDF names are user-controlled and cannot reliably identify entry starts. Large directories can therefore pay a rescan cost after mutation or seek. Corrupt directory entries surface through iterator errors. Hidden/deleted mount flags change visible results. Allocation of the temporary name buffer can fail with `-ENOMEM`.

## Test Signals

Tests should exercise normal iteration, seeking and resuming after directory changes, dot/dotdot handling, hidden/deleted visibility flags, malformed directory entries from `directory.c`, long/Unicode filename conversion failures, and fsync/ioctl operation-table wiring on directory files.
