<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_request.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_request.c

## Purpose
Implements the i915 GPU request lifecycle: allocation, dma-fence integration, dependency waits, semaphore emission, scheduler queueing, hardware submission/unsubmission, retirement, watchdog handling, and wait/debug helpers.

## Important APIs, types, and functions
- DMA fence ops: `i915_fence_ops`, `i915_fence_signaled()`, `i915_fence_enable_signaling()`, `i915_fence_wait()`, and `i915_fence_release()`.
- Lifecycle APIs: `__i915_request_create()`, `i915_request_create()`, `__i915_request_commit()`, `i915_request_add()`, `__i915_request_queue()`, `__i915_request_submit()`, `__i915_request_unsubmit()`, `i915_request_retire()`, and `i915_request_retire_upto()`.
- Dependency APIs: `i915_request_await_dma_fence()`, `i915_request_await_deps()`, `i915_request_await_object()`, `i915_request_await_execution()`, and internal semaphore/execute-callback helpers.
- Error/wait/debug APIs: `i915_request_set_error_once()`, `i915_request_mark_eio()`, `i915_request_cancel()`, `i915_request_wait_timeout()`, `i915_request_wait()`, `i915_request_show()`, and `i915_test_request_state()`.
- Module cache setup/teardown: `i915_request_module_init()` and `i915_request_module_exit()`.

## Control flow
Request creation pins the context, allocates from an RCU-safe slab or reserved engine pool, obtains a timeline seqno, initializes the embedded dma fence and software fences, reserves ring space, invokes the engine allocator, marks the context active, and links the request into the timeline.

Dependency setup decomposes fence arrays, skips same-context waits, squashes already-synchronized timelines through the syncmap, and distinguishes i915 internal waits from external dma fences. Internal waits may emit GPU semaphores when both engines share the same GGTT, semaphores are allowed, the dependency is not an external error-propagating chain, and the waiter is not already busywaiting on that engine. Execution dependencies use irq-work callbacks tied to the signaler's transition to active/inflight.

Commit emits the final breadcrumb reservation, adds ordering against the previous timeline request or parallel parent relationship, and then queueing commits the semaphore and submit software fences. When the submit fence completes, `submit_notify()` arms the watchdog if needed and calls the engine backend `submit_request()` under RCU. Submission sets ACTIVE, moves the request into engine active tracking, emits final breadcrumbs, notifies execute callbacks, and enables breadcrumbs if dma-fence signaling was requested. Unsubmission clears ACTIVE and cancels breadcrumbs during preemption/unwind.

Retirement requires hardware completion, traces retirement, cancels the watchdog, updates ring head, signals the dma fence, updates RPS boost accounting, removes active tracking, unpins/exits the context, finalizes scheduler nodes, and drops the final request reference. Wait paths first optimistic-spin for running requests, may boost RPS for priority waits, attach dma-fence callbacks, flush submission if useful, and sleep with dma-fence semantics.

## State and persistence
Persistent request state lives in `struct i915_request`: dma-fence seqno/context/error/flags, context/engine/ring/timeline pointers, submit and semaphore software fences, scheduler node/dependencies, ring offsets, HWSP pointer, watchdog timer, capture list, GuC priority, and debug/selftest fields. Allocation uses RCU-safe slab reuse and never zeroes whole requests, so every reused field must be explicitly initialized or validated. Timeline ordering and syncmap state persist outside this file.

## Dependencies and integration points
Depends on dma-fence arrays/chains, i915 software fences, scheduler nodes, intel context/timeline/ring/engine backends, breadcrumbs, RPS, reset lockdep maps, HuC delayed load fences, GEM reservation objects, VMA resources, and tracepoints. It is the central integration point between execbuf/GEM submission, GT backend scheduling, user-visible dma fences, and retirement.

## Risks
This file is highly concurrency-sensitive. RCU slab reuse, unstable virtual-engine `rq->engine` pointers, timeline lock requirements, preempt-to-busy races, semaphore error propagation, and callback ordering can produce use-after-free, missed wakeups, deadlocks, or out-of-order execution if changed casually. Fatal error handling must scrub payloads without losing breadcrumbs. Wait semantics differ subtly between `i915_request_wait_timeout()` and `i915_request_wait()` for timeout zero.

## Test signals
Signals include request tracepoints, dma-fence wait/timeout behavior, i915 selftests under `selftests/i915_request.c`, semaphore and external fence dependency tests, GPU reset/error injection, GuC and execlists submission paths, RPS wait boost accounting, HuC delayed-load media submissions, and stress tests with virtual/parallel contexts and preemption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_request.c -->
