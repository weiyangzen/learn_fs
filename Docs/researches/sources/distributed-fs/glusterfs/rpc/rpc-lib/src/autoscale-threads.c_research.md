## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/autoscale-threads.c

Purpose: provides a small helper to adjust RPC service event-thread counts.

Important API: `rpcsvc_autoscale_threads(glusterfs_ctx_t *ctx, rpcsvc_t *rpc, int incr)` increments `ctx->event_pool->auto_thread_count` and calls `gf_event_reconfigure_threads` with current `eventthreadcount + incr`.

Control flow: the function reads the event pool, computes the new requested thread count, updates accounting, and asks the event layer to reconfigure. The `rpc` argument is not used in this implementation.

State and persistence: mutates in-memory event-pool counters and thread configuration. No persistent state.

Dependencies and integration: depends on `glusterfs/gf-event.h` and `rpcsvc.h`. It is part of `libgfrpc` and can be used by RPC services reacting to load.

Risks: no validation prevents negative counts or inconsistent `auto_thread_count` if reconfiguration fails. Callers must supply sensible increments and a valid context/event pool.

Test signals: event-pool reconfiguration tests with positive and negative increments, plus failure-path tests for `gf_event_reconfigure_threads`.
