# sources/distributed-fs/openafs/src/afs/afs_init.c

## Purpose
`afs_init.c` initializes and tears down the main AFS Cache Manager resources. It establishes cache parameters, cache metadata files, volume and dcache/vcache pools, core locks, callback services, cell/server/user tables, sysname state, DNLC state, and platform-specific cache device handles.

## Important APIs, types, and functions
Key exported state includes `cacheDev`, `cacheInfoModTime`, `afs_cacheVfsp` or platform equivalents, `Initialafs_freeVolList`, `afs_memvolumes`, `afs_discon_lock`, `cm_initParams`, `afs_cacheinit_flag`, and `afs_resourceinit_flag`. Major functions are `afs_CacheInit`, `afs_ComputeCacheParms`, `afs_LookupInodeByPath`, `afs_InitCellInfo`, `afs_InitVolumeInfo`, `afs_InitFHeader`, `afs_InitCacheInfo`, `afs_ResourceInit`, `shutdown_cache`, `shutdown_vnodeops`, `shutdown_AFS`, plus private `shutdown_server`, `shutdown_volume`, and AIX `afs_procsize_init`.

## Control flow
`afs_CacheInit` records the Cache Manager epoch, applies dynamic-vcache settings, prevents double initialization, initializes global locks and disconnection queues, initializes DNLC, allocates the volume free list, sets cache counts, initializes vcache and dcache layers, optionally saves Linux credentials for future cache-file access, records VM mapping limits, optionally probes AIX proc size, and stores a `cm_initParams` snapshot for pioctl queries.

`afs_InitCacheInfo` is UFS-cache specific. It locates the cache info file, discovers filesystem fragment size, captures device/vnode identity, opens the cache metadata file, validates or rewrites the `afs_fheader`, truncates invalid contents, and leaves the file open in `afs_cacheInodep` for later slot operations. `afs_InitVolumeInfo` locates and truncates the volume metadata file; BSD variants hold the vnode to avoid lock recursion through vnode reclamation.

`afs_ResourceInit` initializes global locks, cell and callback queues, file-server callback tables, sysname state, Rx server security, and Rx services for callbacks and stats. Shutdown reverses much of this state, freeing volumes, users, tokens, exporters, servers, server addresses, Rx services/events, sysnames, and cache metadata.

## State and persistence behavior
The file configures both persistent cache metadata and in-memory resource pools. Persistent state includes cache info file headers, volume info file contents, cache inode/device identity, and filesystem fragment sizing used in cache accounting. In-memory state includes volume arrays, user/server hash tables, dcache/vcache pools, locks, disconnection queues, sysname data, PAG epoch/counter reset on cache shutdown, and saved Linux cache credentials.

## Dependencies and integration points
Dependencies include OS lookup/statfs/vnode APIs, cache file operations, dcache/vcache initialization, DNLC, cell/server/user modules, callback queue, Rx/RxStats services, sysname initialization, memory cache flags, and platform-specific vnode/device helpers. It is invoked by afsd/kernel module startup and shutdown paths and provides the foundation expected by fetch/store, pioctl, NFS translator, and callback code.

## Risks and edge cases
Initialization order is explicitly critical. Calling cache init twice is intentionally ignored after the first pass, but partially failed dcache initialization leaves earlier allocations in place. UFS cache metadata validation must match chunk sizes and version or the cache file is rewritten. Platform branches hold vnodes or saved credentials to avoid reclaim/security failures. Shutdown assumes write-through of dcache slots succeeds and has comments noting memcache volume allocations may not all be recoverable.

## Test signals
Signals include successful cold start with UFS and memory cache, invalid cache info header rewrite, correct `cm_initParams`, Linux security-module cache-file access using saved credentials, BSD vnode hold/release on shutdown, Rx callback/stat service startup, and clean teardown without leaked users, volumes, server addresses, or DNLC state.
