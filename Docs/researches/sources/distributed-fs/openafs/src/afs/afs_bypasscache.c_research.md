# sources/distributed-fs/openafs/src/afs/afs_bypasscache.c

Purpose: Implements optional cache-bypass reads, where file data is fetched directly into VM/user pages instead of being stored in the AFS disk cache. It also handles transitions between cached and bypass states for a vnode.

Important APIs and functions: `afs_alloc_ncr`/`afs_free_ncr` manage `nocache_read_request` packets. `afs_TransitionToBypass` flushes/stales a vnode and marks `FCSBypass`. `afs_TransitionToCaching` clears bypass mode and discards transient pages/cache hints. `afs_ReadNoCache` verifies the vnode and queues a `BOP_FETCH_NOCACHE` background request. `afs_PrefetchNoCache` performs the FetchData RPC. `afs_NoCacheFetchProc` consumes RX data and copies it into page iovecs, releasing pages as they are filled.

Control flow: Transition-to-bypass takes the GLOCK and vnode write lock, optionally stores dirty segments for writers, stales cache status, smushes cache chunks, frees link data, and sets desired/manual state bits. Read dispatch creates a request, verifies vcache status, and retries background queue insertion with short waits. The prefetch worker obtains an AFS connection, starts 64-bit FetchData when supported with fallback to 32-bit, reads the streaming length/data protocol, copies RX iovecs into page mappings, ends the call, runs `afs_Analyze` for retryable failures, and finally applies returned status with `afs_ProcessFS`.

State and persistence: Global policy is `cache_bypass_strategy`, `cache_bypass_threshold`, and `cache_bypass_prefetch`. Per-vcache state uses `cachingStates`, `cachingTransitions`, callback/server pointer, dirty state, and link-data ownership. Bypass reads intentionally avoid populating persistent disk cache chunks; only metadata/status updates remain.

Dependencies and integration points: Compiled under `AFS_CACHE_BYPASS` or `UKERNEL`. Depends on RX, FetchData stubs, background queueing, vnode/cache invalidation, Linux page locking and kmap APIs, `afs_Analyze`, `afs_conn.c`, and `afs_bypasscache.h` policy macros.

Risks: Page lifetime handling is high risk: every error path must unlock and drop page refs exactly once. The copy loop tracks RX iovec and page offsets manually and assumes page/iovec lengths line up with the requested length. Transition paths take the GLOCK internally and can conflict with callers that already hold locks incorrectly. 64-bit fallback and foreign multi-block fetch handling need server-compatibility coverage.

Test signals: Allocate/free requests with zero and many pages, transition both directions with dirty writers and symlink link data, queue saturation returning `EBUSY`, 64-bit and 32-bit FetchData, short RX read, oversized length rejection, foreign multi-block reads, page release on every error path, and status update after successful bypass fetch.
