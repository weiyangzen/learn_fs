# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_gc.c

Purpose: implements asynchronous garbage collection for PTLRPC security contexts and policy-owned security objects. It lets policy code hand off contexts that must be released in sleepable context and periodically invokes per-policy context cache GC.

Important APIs/types/functions: `sptlrpc_gc_add_sec()` inserts a `ptlrpc_sec` with a policy `gc_ctx` operation and interval into the global sec GC list; `sptlrpc_gc_del_sec()` removes it and synchronizes with any in-progress scan; `sptlrpc_gc_add_ctx()` queues a client context for deferred release and wakes the worker; `sec_process_ctx_list()` drains deferred contexts; `sec_do_gc()` invokes policy `gc_ctx` when `ps_gc_next` expires; `sec_gc_main()` is the delayed work callback; `sptlrpc_gc_init()` schedules the worker and `sptlrpc_gc_fini()` cancels it.

Control flow: the delayed worker first drains the one-shot context handoff list, then iterates the registered security-object list under `sec_gc_mutex`. If a deletion is pending, it drops the mutex and restarts so `sptlrpc_gc_del_sec()` can complete quickly. After scanning it drains contexts again and reschedules itself for the fixed 30-minute interval. Direct context handoff uses `mod_delayed_work(..., 0)` to run promptly rather than waiting for the interval.

State/persistence: global state consists of `sec_gc_list`, `sec_gc_ctx_list`, their spinlocks, `sec_gc_mutex`, the delayed work item, and `sec_gc_wait_del`. It persists only for the module lifetime. Contexts placed on the GC list are expected to hold a single reference that the worker drops with `sptlrpc_cli_ctx_put(ctx, 1)`.

Dependencies/integration: depends on kernel workqueues, Lustre context refcounting from `sec.c`, policy `gc_ctx` callbacks, `ps_gc_interval`/`ps_gc_next` fields in `ptlrpc_sec`, and exported context release APIs. Policies with zero GC interval, such as null/plain in this subset, do not register periodic GC.

Risks/test signals: deletion synchronization is correctness-critical because a sec could otherwise be destroyed while the worker is iterating it. The worker uses a fixed interval rather than the nearest expiry, so GC may be delayed up to 30 minutes. Tests should exercise add/delete while GC is running, queued context release, fini cancellation, refcount expectations, and a policy `gc_ctx` callback that advances `ps_gc_next`.
