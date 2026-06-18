# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/dm_pcache.h

## Purpose
Declares the top-level `dm-pcache` target context and per-bio request object shared between the target front end and cache/backing/cache-device layers. It also centralizes container conversions, target state constants, request reference APIs, deferred-request wakeup, and target-scoped logging macros.

## Important APIs, Types, And Functions
`struct dm_pcache` embeds `pcache_cache_dev`, `pcache_backing_dev`, `pcache_cache`, and `pcache_cache_options`, plus the device-mapper target pointer, deferred-request list/work item, workqueue, state, in-flight request counter, and waitqueue. `struct pcache_request` stores the originating `bio`, byte offset, data length, request refcount, latched return code, and list node for deferral.

Macros `CACHE_DEV_TO_PCACHE`, `BACKING_DEV_TO_PCACHE`, and `CACHE_TO_PCACHE` provide ownership lookup. `PCACHE_STATE_RUNNING` and `PCACHE_STATE_STOPPING` define target lifecycle states, while `pcache_is_stopping()` is used by background workers to stop safely. `pcache_req_get()`, `pcache_req_put()`, and `pcache_defer_reqs_kick()` are implemented in `dm_pcache.c`.

## Control Flow
The header is included by pcache submodules that need to reach the containing target for logging, stop-state checks, or request completion. A bio becomes a `pcache_request` in the target map callback, is passed to cache handling, may be queued on the deferred list, and finally completes through `pcache_req_put()`.

## State And Persistence
All declarations here describe volatile in-memory state. Persistent state is held by the embedded cache device mapping and cache metadata structures declared elsewhere. The request `ret` field latches the first nonzero error so asynchronous pieces can report a single final bio status.

## Dependencies And Integration Points
The header depends on the device-mapper public API and `dm-core.h`. It is the glue between the DM target, cache-device code, backing-device request code, and cache policy/data code. Logging macros prefix messages with the mapped device name through `pcache->ti->table->md->name`.

## Risks
Because `struct dm_pcache` embeds major subsystem objects directly, include ordering and forward declarations must stay consistent with the actual complete type definitions. Request refcount misuse in any submodule can break target teardown because `dm_pcache.c` waits on `inflight_reqs`. The state check is a simple atomic equality test, so callers must still coordinate their own queues and work cancellation.

## Test Signals
Build coverage is the main signal for this header. Runtime signals include clean target teardown with no in-flight hang, correct logging prefixes from all submodules, and correct bio completion after asynchronous cache/backing activity.
