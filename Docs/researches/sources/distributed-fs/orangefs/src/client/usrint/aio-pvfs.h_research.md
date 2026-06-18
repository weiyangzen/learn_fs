# sources/distributed-fs/orangefs/src/client/usrint/aio-pvfs.h
## sources/distributed-fs/orangefs/src/client/usrint/aio-pvfs.h

**Purpose:** Declares OrangeFS POSIX AIO wrapper functions.

**APIs and control flow:** Exposes `pvfs_aio_cancel`, `pvfs_aio_error`, `pvfs_aio_read`, `pvfs_aio_return`, `pvfs_aio_write`, and `pvfs_lio_listio`. `aio_fsync` and `aio_suspend` declarations are commented out, matching unimplemented features.

**State and dependencies:** Includes `aio.h` and relies on the `struct aiocb` ABI used by `aio-pvfs.c`.

**Risks and tests:** `pvfs_aio_cancel` is declared but commented out in the implementation, creating a potential link failure if used. Header/API tests should verify exported symbols match declarations, and feature tests should document unsupported cancel/fsync/suspend behavior.
