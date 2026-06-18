<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.c

## Purpose
Initializes and flushes Mali L2 cache IP blocks used by GP and PP pipes.

## Important APIs, types, and functions
Exports `lima_l2_cache_init()`, `lima_l2_cache_fini()`, `lima_l2_cache_resume()`, `lima_l2_cache_suspend()`, and `lima_l2_cache_flush()`. Internal helpers are `lima_l2_cache_wait_idle()` and `lima_l2_cache_hw_init()`.

## Control flow
Init filters out `l2_cache2` unless PP4-PP7 are present, initializes the spinlock, reads and logs cache geometry, flushes the cache, enables access and read allocation, and sets max reads. Flush serializes with the IP lock, issues clear-all, waits until command busy clears, and returns timeout errors. Resume redoes hardware init.

## State and persistence
Per-cache lock lives in `ip->data.lock`. Hardware enable, max-read, and cache contents persist until reset, flush, or power loss.

## Dependencies and integration points
Depends on register constants and device IP discovery. Scheduler pipes reference L2 cache IPs and flush them around task execution through scheduler code.

## Risks
Flush timeout indicates stuck hardware and can compromise memory coherency. Cache2 presence detection must match Mali450 PP topology. Locking only serializes driver-issued cache commands.

## Test signals
Probe logs of cache size, L2 flush success, multi-cache Mali450 rendering, suspend/resume reinit, and timeout fault injection validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_l2_cache.c -->
