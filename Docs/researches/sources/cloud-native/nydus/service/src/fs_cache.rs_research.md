# sources/cloud-native/nydus/service/src/fs_cache.rs

Purpose: implements the userspace side of Linux cachefiles/fscache on-demand mode for RAFS/EROFS. `FsCacheHandler` opens `/dev/cachefiles`, binds the cache directory/tag, receives kernel `OPEN`, `CLOSE`, and `READ` messages, maps fscache objects to blob/bootstrap sources, and feeds data back to the kernel cache.

Important APIs/types: `FsCacheOpCode`, `FsCacheMsgHeader`, `FsCacheMsgOpen`, `FsCacheMsgRead`, `FsCacheBootstrap`, `FsCacheBlobCache`, `FsCacheObject`, `FsCacheState`, and public `FsCacheHandler::{new, working_threads, stop, run_loop, get_file, cull_cache}`. Message parsers use unaligned little/native reads and length validation before dispatch.

Control flow: `new` configures cachefiles with `dir`, optional `tag`, and `bind ondemand`, or sends `restore` when handed an upgrade fd. `run_loop` polls the cachefiles fd and a waker. `handle_open_request` resolves `volume_key` and `cookie_key` to a blob-cache config; data blobs create a cache object and spawn lazy blob-cache initialization with retry and optional prefetch, while bootstrap opens/copies metadata into the kernel cache after `copen`. `READ` fetches uncompressed blob ranges or mmaps bootstrap data, then sends `fscache_cread`; `CLOSE` tears down blob state and triggers factory GC.

State and persistence: tracks object-id to cache object/fd and object-id to config maps under a mutex. Kernel cache files persist under `<work_dir>/cache`; blob-cache instances are transient but share factory config. Upgrade support keeps the cachefiles fd clone through `get_file`. `cull_cache` walks cachefiles volume directories and uses `inuse`/`cull` commands from the proper working directory.

Dependencies and integration: depends on `BlobCacheMgr`, `BLOB_FACTORY`, `ASYNC_RUNTIME`, `BlobPrefetchRequest`, Linux cachefiles ioctls, `mio`, libc fd reads/writes/mmap/pwrite, and generated blob keys. It is owned by `singleton.rs` and exposed through `FsCacheHandler` on Linux.

Risks: unsafe fd ownership is delicate (`from_raw_fd` plus `mem::forget`), cachefiles protocol parsing assumes host endianness/layout, `cull_cache` changes process cwd, blob-cache initialization is asynchronous so early reads may see "not ready", and prefetch/error handling often logs instead of failing the open. Cache hash/path logic must match kernel cachefiles layout exactly.

Test signals: tests validate opcode/header/open/read parsing failures, UTF-8 handling, helper hash/rotate/rounding behavior, cookie path determinism, max-value reads, and local handler construction. Real cachefiles behavior still requires root, a new enough kernel, and `/dev/cachefiles` integration tests through the singleton service.
