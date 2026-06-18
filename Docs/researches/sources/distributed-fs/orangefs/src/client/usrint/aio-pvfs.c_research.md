# sources/distributed-fs/orangefs/src/client/usrint/aio-pvfs.c
## sources/distributed-fs/orangefs/src/client/usrint/aio-pvfs.c

**Purpose:** Provides POSIX AIO-style OrangeFS entry points that adapt `struct aiocb` calls into the internal `aiocommon` asynchronous I/O engine.

**APIs and control flow:** `pvfs_aio_error()` validates `aiocbp` and its backpointer in `__next_prio`, then returns `__error_code`. `pvfs_aio_read()` and `pvfs_aio_write()` set `aio_lio_opcode` and submit one control block through `pvfs_lio_listio(LIO_NOWAIT, ...)`. `pvfs_aio_return()` validates completion, removes/frees the internal `pvfs_aiocb`, nulls the backpointer, and returns `__return_value`. `pvfs_lio_listio()` validates mode/count/list, allocates a `pvfs_aiocb` array, wraps each non-null aiocb, stores the mutual backpointer, and calls `aiocommon_lio_listio()`.

**State and dependencies:** Depends on glibc aiocb internal fields (`__next_prio`, `__error_code`, `__return_value`), `aiocommon`, errno, and gossip.

**Risks and tests:** Uses nonportable private `struct aiocb` members. Null entries in `pvfs_lio_listio()` mutate `nent` while iterating and can corrupt indexing. Allocation failure leaks earlier allocations. `sig` and `LIO_WAIT` are TODO. Tests should cover null entries, max list size, allocation failures, read/write completion, return-before-complete, repeated return/error, and portability against target libc.
