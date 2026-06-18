# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/context.c

## Purpose
Owns HabanaLabs context lifetime. It creates per-file user contexts, initializes kernel and user context state, manages ASIDs, VM/CB VA resources, pending CS fence rings, recent outcome storage, timestamp-registration locking, and encapsulated-signal reservation handles. It also provides the fence lookup APIs used by command submission and wait ioctls.

## Important APIs, Types, And Functions
Context lifecycle entry points are `hl_ctx_create()`, `hl_ctx_init()`, `hl_ctx_do_release()`, `hl_ctx_put()`, `hl_ctx_get()`, `hl_get_compute_ctx()`, `hl_ctx_mgr_init()`, and `hl_ctx_mgr_fini()`. Fence lookup APIs are `hl_ctx_get_fence()` and `hl_ctx_get_fences()`, both built on `hl_ctx_get_fence_locked()`.

Encapsulated signal cleanup is implemented by `encaps_handle_do_release()`, `hl_encaps_release_handle_and_put_ctx()`, `hl_encaps_release_handle_and_put_sob()`, and `hl_encaps_release_handle_and_put_sob_ctx()`. The per-context signal manager is initialized and finalized by `hl_encaps_sig_mgr_init()` and `hl_encaps_sig_mgr_fini()`.

## Control Flow
`hl_ctx_create()` allocates a context, inserts it into the file-private context IDR, initializes it as a user context, takes a reference on the owning `hl_fpriv`, and stores it as the active compute context. `hl_ctx_init()` initializes common state first: refcount, sequence number, CS lock, context-switch tokens, pending fence array, outcome-store free list/hash, and hardware-block memory tracking. Kernel contexts receive ASID 0 and initialize VM/MMU plus ASIC context state. User contexts allocate a free ASID, initialize VM, CB VA pool, ASIC context state, encapsulated signal manager, and timestamp-registration mutex.

Release flows are reference-counted. `hl_ctx_do_release()` calls `hl_ctx_fini()`, clears `hpriv->ctx` under `ctx_lock`, drops the `hpriv` reference, and frees the context. `hl_ctx_fini()` releases all pending fences in the ring, finalizes debug/coresight state for user contexts, calls ASIC context cleanup, finalizes decoder context state, CB VA pool, VM, ASID, encapsulated signal manager, and timestamp mutex. Kernel context cleanup instead finalizes ASIC context, VM, and MMU state.

Fence lookup is ring-based. A sequence greater than or equal to `ctx->cs_sequence` is invalid, a sequence older than `max_pending_cs` is considered gone, and an in-window sequence returns the fence in `ctx->cs_pending[seq & (max_pending_cs - 1)]` with an added fence reference. `hl_ctx_get_fences()` performs multiple lookups under a single `cs_lock` and releases already acquired fences on error.

## State And Persistence
Persistent context state includes `asid`, `handle`, `cs_sequence`, `cs_pending[]`, `outcome_store`, context-switch tokens, VM mappings, CB VA pools, hardware-block mappings, encapsulated signal IDR, and timestamp registration lock. The context manager state is an IDR protected by a mutex inside `hl_fpriv`. The compute context is also visible through `hdev->fpriv_list` and `hpriv->ctx`.

Encapsulated signal handles persist in `ctx->sig_mgr.handles` until unreserved, consumed by CS completion, or cleaned during context/device release. Cleanup may optionally put the hardware SOB reference and/or the context reference depending on which release callback is used.

## Dependencies And Integration Points
The file integrates with ASID allocation, VM/MMU initialization, CB VA pool management, decoder context cleanup, Coresight debug mode, hardware-block memory tracking, command-submission fence waits, and file-private lifetime in `device.c`. It calls ASIC-specific `ctx_init()` and `ctx_fini()` hooks. `hl_get_compute_ctx()` coordinates with `hdev->fpriv_list_lock` and `hpriv->ctx_lock`, which makes it an important bridge between device-level reset paths and per-context resources.

## Risks
The fence ring intentionally reuses slots, so callers must correctly distinguish invalid, gone, and live fences. A caller that assumes `NULL` means error could mis-handle old completed CSs. Context release relies on every active CS and pending interrupt holding references; missing references elsewhere can allow `hl_ctx_fini()` to run while asynchronous work still dereferences the context.

Encapsulated signal finalization is subtle because different paths own different combinations of SOB and context references. `hl_encaps_sig_mgr_fini()` expects rollback to have emptied the IDR and logs a warning if handles remain, then puts SOB references without putting context references. Ordering with `idr_for_each_entry()` plus kref callbacks that remove from the same IDR should remain carefully reviewed.

## Test Signals
Coverage should include user context create/destroy, kernel context init/fini, ASID exhaustion, ASIC `ctx_init()` failure unwinding, pending fence lookup for live/future/gone sequences, multi-fence lookup error unwind, release with outstanding CS fences, release while debug mode is active, encapsulated signal handle leak cleanup, and reset paths that call `hl_get_compute_ctx()`. Debug logs for user/kernel context close, warnings about leftover encapsulated signal handles, and fence wait behavior on gone sequences are useful runtime signals.
