<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_request.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_request.h

## Purpose
Declares the i915 request object, request fence flags, request lifecycle APIs, wait helpers, dependency APIs, and inline state predicates used across GEM and GT submission.

## Important APIs, types, and functions
- `struct i915_request` embeds `struct dma_fence`, software fences, scheduler node/dependency storage, context/engine/ring/timeline pointers, HWSP seqno pointer, ring offsets, watchdog state, capture list, and GuC priority state.
- Fence flags include ACTIVE, PQUEUE, HOLD, INITIAL_BREADCRUMB, SIGNAL, NOPREEMPT, SENTINEL, BOOST, SUBMIT_PARALLEL, SKIP_PARALLEL, and COMPOSITE.
- Public helpers include creation, commit, queue, submit/unsubmit, cancel, retire, wait, dependency await, request display, active-engine lookup, module init/exit, and `i915_test_request_state()`.
- Inline predicates cover signaled/active/ready/running/started/completed, hold/nopreempt/sentinel/boost, timeline/context dereference, active HWSP offset, and request get/put.

## Control flow
The header has mostly inline control flow. Completion and start checks first trust the dma-fence signaled bit when available, otherwise read the HWSP seqno under RCU because the HWSP may be freed. Timeline/context accessors are protected by timeline mutex, scheduler-engine lock, or parking context conditions. `to_request()` assumes the dma fence is the first struct member.

## State and persistence
The structure defines all durable per-request state until final dma-fence release. RCU reuse constraints mean fields can contain old values until explicitly reset during creation. `i915_request_mark_complete()` decouples completed requests from HWSP by pointing the seqno pointer at the fence seqno.

## Dependencies and integration points
Included by scheduler, engine backends, GEM exec/object synchronization, breadcrumbs, reset, tracepoints, selftests, and VMA resource capture code. It depends on DMA fence, hrtimer, lockdep, Intel context/engine/timeline types, scheduler, software fences, selftest declarations, and VMA resource helpers.

## Risks
Inline state predicates are used in lockless and RCU-sensitive paths. Changing struct layout, fence flags, or HWSP read rules can break dma-fence casting, signal detection, scheduler membership checks, or active request lookup. The active timeline accessor is valid only under submission-time pinning assumptions.

## Test signals
Compile coverage catches struct/API drift. Runtime validation comes from request selftests, lockdep, KCSAN-style race testing, scheduler/preemption tests, request state debug output, and tracepoint consistency across add/submit/execute/retire/wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_request.h -->
