# sources/distributed-fs/lustre-release/lustre/osc/osc_internal.h research

## Purpose
`osc_internal.h` is the private OSC interface header shared by the files in this directory. It does not define the main private structs; those come from `<lustre_osc.h>`, which is external to the listed source set. Instead, this header declares cross-file functions, global caches/device symbols, quota hooks, shrinker hooks, and small helpers used by cache, page, object, IO, lock, and request paths.

## Important APIs, Types, and Functions
The header declares cache/writeback interfaces such as `osc_extent_finish()`, `osc_extent_release()`, `osc_build_rpc()`, `osc_send_empty_rpc()`, `osc_lru_reserve()`, `osc_lru_unreserve()`, `osc_lock_discard_pages()`, and `osc_ldlm_hp_handle()`. Lock/RPC wrappers include `osc_enqueue_base()`, `osc_match_base()`, `osc_setattr_async()`, `osc_fallocate_base()`, `osc_sync_base()`, and `osc_ladvise_base()`. Device/object interfaces include `osc_setup()`, `osc_tunables_init()`, `osc_device_type`, and `osc_object_alloc()`.

Helpers include `osc_env_new_io()`, which zeroes and returns `osc_env_info(env)->oti_io`; `osc_recoverable_error()`, which classifies `-EIO`, `-EROFS`, `-ENOMEM`, `-EAGAIN`, and `-EINPROGRESS`; `rpcs_in_flight()`, which sums client read/write RPCs; `list_empty_marker()` for debug output; `osc_max_write_chunks()`, which limits write RPC chunk spread to `PTLRPC_MAX_BRW_SIZE >> cl_chunkbits`; and `osc_set_io_portal()`, which selects MDS or OST IO portal based on `IBITS` connection data.

## Control Flow
The header sets the call graph boundaries. `osc_io.c` calls cache APIs declared here to submit pages, reserve LRU slots, flush fsync ranges, and touch page attributes. `osc_lock.c` calls cache discard/writeback and matching/enqueue base helpers. `osc_page.c` calls cache queue/teardown helpers and LRU reservation. `osc_object.c` calls lock matching and cache invalidation helpers. `osc_request.c` is expected to provide the lower RPC base functions and `osc_build_rpc()`.

## State and Persistence Behavior
The header declares global request-pool state (`osc_pool_req_count`, `osc_reqpool_maxreqcount`, `osc_rq_pool`), slab cache descriptors (`osc_caches`), shrinker state (`osc_shrink_list`, `osc_shrink_lock`, `osc_page_cache_shrink_enabled`), and quota/unstable-page interfaces. It does not own persistence. It formalizes access to in-memory client state and RPC request state, which affects when dirty data is sent to OSTs and when unstable pages are considered committed.

## Dependencies and Integration Points
`<lustre_osc.h>` is the key dependency and supplies the struct definitions consumed by every prototype. The header integrates with LDLM (`ldlm_lock`, policy data, match flags), OBD exports/devices/imports, PTLRPC requests and request sets, CLIO (`cl_io`, `cl_object`, priorities), quota control, shrinkers, and LNet/portal selection. The `osc_max_write_chunks()` comment documents a ZFS transaction-size constraint that shapes batching behavior in `osc_cache.c` and `osc_io.c`.

## Risks
Because this is a private cross-file ABI, signature drift can silently break multiple paths. The inline helpers encode policy: misclassifying recoverable errors, write chunk limits, or IO portal selection can affect recovery, performance, and correctness. `osc_env_new_io()` zeroes a reusable environment object; callers must not retain stale pointers across nested CLIO operations.

## Test Signals
Compile coverage is essential because this header fans out across many OSC translation units. Behavioral tests should verify max-write-chunk enforcement for large `cl_chunkbits`, correct portal selection for MDS-vs-OST clients, recoverable error handling in request paths, shrinker enable/disable behavior, and cross-file call compatibility when adding fields or changing request-base helpers.
