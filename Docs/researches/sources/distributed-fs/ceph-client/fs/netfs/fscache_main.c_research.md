<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/fscache_main.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_main.c

## Purpose
Initializes and tears down the FS-Cache subsystem embedded in netfs support. It also defines the stable FS-Cache hash used for volume/cookie keys and exports FS-Cache tracepoints and the global FS-Cache workqueue.

## Important APIs, Types, And Functions
Exports tracepoints `fscache_access_cache`, `fscache_access_volume`, and `fscache_access`, plus `fscache_wq`. Important functions are `fscache_hash()`, `fscache_init()`, and `fscache_exit()`. Internal `HASH_MIX()` and `fold_hash()` implement an architecture-stable hash over little-endian 32-bit words.

## Control Flow
During `fscache_init()`, the code allocates an unbound/freezable workqueue named `fscache`, initializes procfs entries, creates the cookie slab cache, and logs successful load. Error paths unwind procfs and the workqueue. `fscache_exit()` destroys the cookie slab, cleans procfs, shuts down the cookie LRU timer synchronously, destroys the workqueue, and logs unload.

## State And Persistence
Persistent on-disk compatibility depends on `fscache_hash()` being stable; comments note that key hash bits may appear on disk. Runtime state includes `fscache_wq` and `fscache_cookie_jar`. The hash caller must pass data padded to a multiple of four bytes.

## Dependencies And Integration Points
Depends on `internal.h`, module/init APIs, trace/events/fscache, proc initialization, cookie slab allocation, and the LRU timer declared in cookie management. Called from `netfs_init()` when `CONFIG_FSCACHE` is enabled.

## Risks
Changing the hash algorithm breaks cache identity compatibility. Teardown order matters: workers/timers must not outlive slabs or proc entries they reference. Initialization failure must avoid leaving `/proc/fs/netfs` partial FS-Cache files.

## Test Signals
Build/load/unload FS-Cache repeatedly, verify proc entries appear and disappear, tracepoints are exported, workqueue exists, and collision-sensitive volume/cookie keys hash consistently across architectures.
