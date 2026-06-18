# sources/distributed-fs/orangefs/src/client/usrint/aiocommon.h
## sources/distributed-fs/orangefs/src/client/usrint/aiocommon.h

**Purpose:** Internal header for OrangeFS AIO common structures and functions.

**APIs and control flow:** Defines limits (`PVFS_AIO_MAX_RUNNING`, `PVFS_AIO_LISTIO_MAX`), progress states, default timeout, and `struct pvfs_aiocb` containing sys op ID, I/O response, memory/file requests, original aiocb pointer, and qlist link. Declares `aiocommon_init`, `aiocommon_lio_listio`, and `aiocommon_remove_cb`.

**State and dependencies:** Includes pthread, PVFS types, usrint/posix/openfile/iocommon headers, qlist, and gossip. The struct is the bridge between public `struct aiocb` and sysint async I/O completion.

**Risks and tests:** Limits are compile-time constants and may not match workload expectations. The public-to-internal pointer linkage is handled outside this header through private aiocb fields. Compile tests should ensure all included types are available across supported platforms; runtime tests should validate max-running and list-size behavior.
