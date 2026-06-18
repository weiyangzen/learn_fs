# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmdbuf.c

## Purpose
Implements the SVGA command-buffer manager used for asynchronous command submission. It allocates inline or pooled command-buffer space, submits buffers to hardware contexts, processes completion/preemption/error statuses, handles deferred error recovery, manages idle/allocation waiters, and owns command-buffer pool lifetime.

## Important APIs, Types, And Functions
- `struct vmw_cmdbuf_man` stores locks, work item, context queues, error list, DRM range manager, optional MOB/DMA pool backing, current small-command buffer, DMA pools for headers, wait queues, IRQ state, and hardware limits.
- `struct vmw_cmdbuf_context` has submitted, hardware-submitted, and preempted queues plus submission blocking state.
- `struct vmw_cmdbuf_header` describes one command buffer and its device header.
- `vmw_cmdbuf_alloc()`, `vmw_cmdbuf_reserve()`, and `vmw_cmdbuf_commit()` are the main allocation/submission APIs.
- `vmw_cmdbuf_cur_flush()` and `vmw_cmdbuf_idle()` flush and wait for completion.
- `vmw_cmdbuf_set_pool_size()`, `vmw_cmdbuf_remove_pool()`, `vmw_cmdbuf_man_create()`, and `vmw_cmdbuf_man_destroy()` manage bootstrap, pool, and teardown.

## Control Flow
Small submissions use a shared current command buffer protected by `cur_mutex`; larger ones allocate a dedicated header and space. Inline submissions use a DMA pool object containing header plus command bytes; pooled submissions allocate a range from `drm_mm` backed by coherent DMA memory or a pinned MOB. Commit flushes current work when requested, then queues the header to a context. Processing submits until the hardware queue limit, walks completed hardware buffers, frees successful ones, moves preempted ones, and defers command errors to workqueue context.

The error worker describes and skips the failing command when possible, blocks all contexts, preempts hardware, splices preempted buffers after the repaired buffer, restarts contexts, and emits a replacement fence if one was discarded.

## State, Persistence, Dependencies, And Integration
State is volatile queue, range-manager, DMA-pool, and wait-queue state. Dependencies include SVGA command-buffer registers, DMA pools, coherent DMA allocation, TTM BOs for MOB-backed pools, DRM MM, vmwgfx waiters, fences, and command-description helpers. It is called by command reserve/commit wrappers, resource/context/cotable binding paths, IRQ threaded handler, device init, and teardown.

## Risks And Test Signals
Risks include deadlocks between current-buffer and pool allocation, missed IRQ enabling/disabling, queue corruption during preemption/error recovery, freeing inline versus pooled headers incorrectly, and pool removal while work remains. Test signals include inline-only bootstrap, MOB-backed and DMA-backed pools, high-priority two-context devices, allocation wait under full pool, command error recovery with multiple queued buffers, preemption status handling, idle timeout, and destroy with `has_pool` already removed.
