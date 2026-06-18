# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_cache.c

Purpose: provides a small non-reentrant read/directory cache for HMC drive FTP transfers, reducing repeated backend reads for `dir`, `nls`, and `get`.

Important APIs/types/functions: `struct hmcdrv_cache_entry` stores command id, filename, file size, cached offset, timeout, content pointer, and cache length. Main functions are `hmcdrv_cache_get()`, `hmcdrv_cache_do()`, `hmcdrv_cache_cmd()`, `hmcdrv_cache_startup()`, and `hmcdrv_cache_shutdown()`.

Control flow: cached commands first try to satisfy the requested file range from a valid, unexpired cache. Misses call the supplied backend transfer function, optionally using the cache buffer as a larger transfer target, update file metadata and content position, and copy requested bytes to the original buffer. Write/error paths invalidate cached read state.

State and persistence behavior: one global cache entry stores transient file metadata and optional DMA-capable content pages. Timeout is 30 seconds. No file data persists beyond module lifetime.

Dependencies and integration points: used by `hmcdrv_ftp_do()` under the FTP mutex; depends on page allocation, jiffies, `hmcdrv_ftp_cmdspec`, and backend function callbacks.

Risks and test signals: global state is not internally locked; correctness depends on external serialization. Cache length uses requested size but allocation uses page order, so effective allocation may be larger than recorded. Test disabled cache, partial range hits/misses, timeout expiry, file-size EOF behavior, write invalidation, backend errors, and startup allocation failure.
