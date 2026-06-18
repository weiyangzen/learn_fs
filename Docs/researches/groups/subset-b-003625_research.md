# subset-b-003625 research

Grouped research for i915 core register definitions, request submission, scheduler primitives, software fences, scatterlist helpers, sysfs/switcheroo/vGPU integration, tracepoints, TTM buddy memory management, user extension parsing, and small utility helpers. Each source file has a delimited section for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg.h

## Purpose
Defines a compact set of i915 MMIO registers and bit fields used by core GT, GTT, interrupt, stolen-memory, clock-gating, power, L3 parity, GSC/HECI, and legacy display/GMBUS-adjacent paths. The file also documents the register macro style used across i915.

## Important APIs, types, and functions
- Register-address macros use `_MMIO()` from `i915_reg_defs.h` and display helpers from `intel_display_reg_defs.h`.
- Important groups include `GU_CNTL`, stolen memory reservation masks, reset registers, IOSF sideband registers, fence registers, ring base offsets, HECI/GSC registers, GT/PCU interrupt triplets, L3 parity registers, GGC/GSM/DSM stolen-memory registers, and MTL stolen-access registers.
- `I915_IRQ_REGS()` and `I915_ERROR_REGS()` group register triplets/pairs for interrupt and error handling callers.

## Control flow
This header is declarative. Runtime code expands these macros to platform-specific MMIO offsets and bit masks, then accesses them through uncore/display register helpers. Function-like macros choose register instances for fence slots, rings, HECI firmware status registers, L3 slices, and GT interrupt banks.

## State and persistence
No C state is stored here. The definitions address persistent hardware state: interrupt masks/status, stolen memory layout, fence registers, power/performance registers, clock-gating bits, and firmware status windows. Incorrect definitions affect hardware state programmed elsewhere.

## Dependencies and integration points
Included by core i915 files such as utility code, uncore/GT code, interrupt handling, stolen-memory probing, GSC/HECI firmware logic, sysfs L3 parity paths, and platform workarounds. It depends on typed register wrappers and generic Intel register bit helpers.

## Risks
The macros are platform-sensitive. Wrong bit shifts or generation-specific reuse can cause invalid MMIO writes, missed interrupts, broken stolen-memory discovery, bad fence tiling setup, or firmware communication failures. Large legacy sections mix raw shifts with newer `REG_BIT`/`REG_GENMASK` style, so edits need careful local consistency.

## Test signals
Build coverage catches type mismatches. Runtime signals include clean MMIO unclaimed-access logs, correct interrupt delivery, stolen-memory size detection, working GSC/HECI status polling, L3 parity sysfs behavior, GT reset handling, and platform workarounds passing on gen2 through Xe-era hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg_defs.h

## Purpose
Provides typed wrappers and small aggregate types for i915 MMIO register definitions.

## Important APIs, types, and functions
- `i915_reg_t` and `_MMIO()` represent ordinary MMIO offsets.
- `i915_mcr_reg_t` and `MCR_REG()` represent multicast/replicated register offsets.
- `INVALID_MMIO_REG`, `i915_mmio_reg_offset()`, `i915_mmio_reg_equal()`, and `i915_mmio_reg_valid()` provide generic offset helpers over both typed wrappers.
- `struct i915_irq_regs`/`I915_IRQ_REGS()` and `struct i915_error_regs`/`I915_ERROR_REGS()` bundle common IMR/IER/IIR and EMR/EIR register sets.

## Control flow
The file has no runtime control flow. `_Generic` selection in `i915_mmio_reg_offset()` preserves type convenience while reducing callers to a raw offset when needed.

## State and persistence
No runtime state is stored. The typed wrappers encode register identity in compile-time constants and local aggregate values.

## Dependencies and integration points
Depends on DRM Intel `pick.h` and `reg_bits.h`. It underpins `i915_reg.h`, GT/display register headers, uncore register accessors, interrupt setup, and MCR register handling.

## Risks
Typed register wrappers rely on callers not discarding the MCR/non-MCR distinction prematurely. `INVALID_MMIO_REG` is offset zero, so any real offset-zero register would need special handling. `_Generic` only supports the explicitly listed wrapper types.

## Test signals
Compile-time coverage is the main signal. Misuse tends to show as type errors, invalid register comparisons, or uncore helpers targeting the wrong access path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg_defs.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.c

## Purpose
Builds and manages refcounted scatter-gather tables for i915 memory ranges represented by DRM MM nodes or TTM buddy allocations.

## Important APIs, types, and functions
- `i915_sg_trim()` shrinks an sg table from `orig_nents` to the effective `nents`.
- `i915_refct_sgt_init()` initializes `struct i915_refct_sgt` with default release ops.
- `i915_rsgt_from_mm_node()` creates a refcounted sg table from a contiguous `drm_mm_node`.
- `i915_rsgt_from_buddy_resource()` creates a refcounted sg table from an `i915_ttm_buddy_resource` block list.

## Control flow
Both constructors allocate an `i915_refct_sgt`, initialize size/refcount/release ops, allocate a worst-case sg table, then fill entries by walking the source range or buddy blocks. Adjacent physical/device ranges are coalesced when offsets are contiguous and the current segment is below the maximum aligned segment size. Final tables are marked with `sg_mark_end()` and trimmed.

## State and persistence
The produced `i915_refct_sgt` persists until its kref reaches zero, then the default release frees the sg table and wrapper. DMA address/length fields encode GPU memory offsets plus `region_start`, not CPU-mapped page ownership.

## Dependencies and integration points
Depends on Linux scatterlist APIs, `drm_mm_node`, `gpu_buddy`, TTM buddy resources, and i915 GEM assertions. Used by memory-region and TTM code that needs refcounted sg tables for LMEM or address-space resources.

## Risks
Segment sizing must respect `UINT_MAX`, page alignment, and sg table entry-count limits. Buddy blocks must be non-empty and sized consistently with resource size. Incorrect coalescing can create DMA segments that cross page-alignment or hardware segment limits.

## Test signals
Selftests under `selftests/scatterlist.c`, allocation failure injection, large resource tests exceeding unsigned int entry counts, mixed contiguous/noncontiguous buddy-block resources, and validation of DMA addresses and lengths against expected region offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.h

## Purpose
Declares optimized scatter-gather iterators, segment-size helpers, and the refcounted sg-table abstraction used by i915 memory managers.

## Important APIs, types, and functions
- `struct sgt_iter` and `__sgt_iter()` track page or DMA-address iteration state.
- Iteration macros include `__for_each_sgt_daddr()`, `__for_each_daddr_next()`, and `for_each_sgt_page()`.
- Segment helpers include `__sg_next()`, `i915_sg_dma_sizes()`, and `i915_sg_segment_size()`.
- `struct i915_refct_sgt_ops` and `struct i915_refct_sgt` provide kref-managed sg tables.
- Declares constructors from DRM MM nodes and TTM buddy resources.

## Control flow
Iterator macros initialize from the first sg entry, yield page or DMA addresses in fixed steps, and advance to the next sg entry when the current entry is exhausted. `__sg_next()` handles chained scatterlists without requiring the generic iterator.

## State and persistence
The header defines the persistent state carried by `i915_refct_sgt`: kref, sg table, byte size, and release ops. Iterator state is stack-local and transient.

## Dependencies and integration points
Depends on Linux scatterlist, DMA mapping, PFN helpers, Xen detection, and i915 GEM assertions. It is used throughout GEM, memory-region, page-table, and TTM code for walking pages/device addresses.

## Risks
Iterator macros rely on page-sized alignment and nonzero DMA lengths. Xen PV forces segment size to PAGE_SIZE because i915 cannot tolerate DMA bounce buffering semantics. Misusing `i915_refct_sgt_get()` on NULL is unsafe; only `put()` tolerates NULL.

## Test signals
Scatterlist selftests, Xen PV mapping tests, page-table population tests across mixed sg entries, DMA segment-size checks on devices with limited mapping sizes, and KASAN/UBSAN coverage for iterator bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.c

## Purpose
Implements i915 scheduler DAG and priority-queue support shared by submission backends.

## Important APIs, types, and functions
- `i915_sched_lookup_priolist()` finds or allocates a priority list in an RB tree.
- `i915_schedule()` and `__i915_schedule()` propagate priority changes through dependency chains.
- `i915_sched_node_init()`, `i915_sched_node_reinit()`, `i915_sched_node_add_dependency()`, `__i915_sched_node_add_dependency()`, and `i915_sched_node_fini()` manage scheduler node dependency lists.
- `i915_request_show_with_schedule()` prints a request and unsatisfied cross-timeline dependencies.
- `i915_sched_engine_create()`, get/put helpers, and module init/exit manage scheduler-engine and slab state.

## Control flow
Priority scheduling starts with a request node and builds a flat DFS list of unsignaled dependencies instead of recursing on the kernel stack. It then walks dependencies in reverse order under the appropriate scheduler-engine lock, updates priorities, moves ready requests between priolists, invokes backend priority bump hooks, and kicks backend submission. Virtual engines are handled by repeatedly checking that the locked scheduler engine still matches the request's current engine.

Dependency addition publishes RCU-visible signaler/waiter links under a global schedule lock and propagates scheduler flags. Finalization removes both incoming and outgoing dependency links and frees allocated dependency records.

## State and persistence
Persistent scheduler state lives in each `i915_sched_node`, allocated `i915_dependency` records, `i915_priolist` RB-tree nodes, and `i915_sched_engine` queues/locks/hooks. Slab caches persist for dependency and priolist allocations.

## Dependencies and integration points
Depends on `i915_request` state predicates, DRM/i915 priorities, submission backend hooks, Linux RB trees, RCU list walking, tasklets, and lockdep. Integrated with request queueing, engine backends, priority inheritance, and debug request printers.

## Risks
The dependency graph must remain acyclic and lock ordering between global schedule lock and per-engine locks is delicate. Allocation failure in a non-normal priolist disables priority lists and falls back to FIFO behavior, which is intentional but can alter scheduling fairness. Virtual-engine `rq->engine` instability requires the relock loop.

## Test signals
Scheduler selftests, priority inheritance tests, virtual engine migration tests, stress with dependency chains, allocation-failure injection for priolist fallback, lockdep, and request debug output showing expected dependency ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.h

## Purpose
Declares scheduler-node, dependency, priority-list, and scheduler-engine helper APIs used by i915 request submission backends.

## Important APIs, types, and functions
- Priolist iteration macros: `priolist_for_each_request()` and `priolist_for_each_request_consume()`.
- Node APIs: init, reinit, add dependency, finish, and schedule.
- Priolist APIs: lookup and free helpers.
- Scheduler-engine APIs: create, get, put, empty/reset checks, active tasklet lock/unlock helpers, disabled check, and module init/exit.
- Debug API: `i915_request_show_with_schedule()`.

## Control flow
Most control flow is inline reference counting, empty checks, and tasklet lock discipline. `i915_sched_engine_active_lock_bh()` disables bottom halves and locks the tasklet to prevent local softirq recursion while manipulating active submission state.

## State and persistence
No additional state is stored here beyond the structures declared in `i915_scheduler_types.h`. Refcount helpers control scheduler-engine lifetime through `kref`.

## Dependencies and integration points
Depends on list/bit/kernel helpers, scheduler types, and i915 tasklet wrappers. Included by request code, GT engine backends, and debug paths.

## Risks
Tasklet locking helpers must pair bottom-half disable/enable correctly. Priolist free must avoid freeing the embedded normal-priority list. Backends must honor scheduler-engine lifetime with get/put.

## Test signals
Build coverage, lockdep on tasklet/bottom-half regions, scheduler-engine lifetime tests, and backend queue manipulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler_types.h

## Purpose
Defines scheduler data structures shared between i915 request objects and submission engines.

## Important APIs, types, and functions
- `struct i915_sched_attr` carries execution priority.
- `struct i915_sched_node` tracks signalers, waiters, queue membership, current attributes, scheduler flags, and semaphore engine mask.
- `struct i915_dependency` links waiter and signaler nodes and carries allocation/external/weak flags.
- `for_each_waiter()` and `for_each_signaler()` provide lockless/RCU dependency iteration.
- `struct i915_sched_engine` holds backend queue state, priolists, locks, tasklet, private data, lifecycle hooks, and priority/preemption hooks.

## Control flow
The file is declarative, but its comments define scheduler semantics: the scheduler is primarily passive DAG tracking plus priority-ordered ready queues, with backend active elements handling timeslicing/preemption decisions.

## State and persistence
Scheduler nodes are embedded in requests and live until request retirement. Dependencies live until removed by node finalization or dependency completion. Scheduler engines persist with backend lifetime and own the RB-tree priority queue and request/hold lists.

## Dependencies and integration points
Depends on Intel engine masks and priolist types. Integrated with `i915_request`, scheduler implementation, execlists/GuC backends, and debug traversals.

## Risks
Dependency list comments describe fundamental invariants: signalers precede waiters, dependencies form a DAG, and list walkers may be lockless/RCU. Adding fields or changing flags requires updates in scheduler propagation, request dependency setup, and backend priority handling.

## Test signals
Priority propagation tests, DAG traversal/debug output, backend preemption behavior, RCU list walking under stress, and lockdep/KCSAN coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_selftest.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_selftest.h

## Purpose
Defines the i915 selftest configuration, declarations, and conditional macros used to compile mock, live, and performance selftests into the driver.

## Important APIs, types, and functions
- `struct i915_selftest` stores timeout, random seed, filter, and mock/live/perf switches.
- When enabled, declares `i915_mock_selftests()`, `i915_live_selftests()`, `i915_perf_selftests()`, generated test functions from selftest headers, `struct i915_subtest`, setup/teardown helpers, and `__i915_subtests()`.
- Macros include `i915_subtests()`, `i915_live_subtests()`, `intel_gt_live_subtests()`, `SUBTEST()`, `I915_SELFTEST_DECLARE()`, `I915_SELFTEST_ONLY()`, `I915_SELFTEST_EXPORT`, `IGT_TIMEOUT()`, and `igt_timeout()`.
- Always declares `__igt_timeout()` and `igt_hexdump()`.

## Control flow
With selftests enabled, included lists of selftest declarations expand through a temporary `selftest(name, func)` macro. Live test wrappers clear GuC scheduler disable delay before invoking the common subtest runner. Without selftests, public entry points become no-op inline stubs and selftest-only declarations disappear.

## State and persistence
Global `i915_selftest` persists module-wide when configured. Timeout values, filters, and flags control test execution. `I915_SELFTEST_DECLARE()` conditionally adds fields to production structures only in selftest builds.

## Dependencies and integration points
Depends on kernel fault injection when enabled, PCI/DRM i915 private types, selftest declaration headers, and intel-gpu-tools conventions. Included broadly by i915 modules that expose selftest-only state or compile local selftest C files.

## Risks
Selftest-only fields must not leak into production ABI assumptions. Generated declarations depend on included selftest headers matching the expected function signatures. Live tests manipulate hardware and need robust setup/teardown to avoid leaving the device wedged.

## Test signals
Running mock/live/perf selftests through the i915 test runner, timeout handling through `igt_timeout()`, filter selection, fault-injection tests, and production builds with selftests disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.c

## Purpose
Implements i915 software fences: lightweight N:M synchronization points used to gate request submission and other asynchronous driver work before dma-fence signaling.

## Important APIs, types, and functions
- Initialization/lifecycle: `__i915_sw_fence_init()`, `i915_sw_fence_reinit()`, `i915_sw_fence_commit()`, optional `i915_sw_fence_fini()`, and `i915_sw_fence_complete()`.
- Dependency APIs: `i915_sw_fence_await()`, `i915_sw_fence_await_sw_fence()`, `i915_sw_fence_await_sw_fence_gfp()`, `i915_sw_fence_await_dma_fence()`, `__i915_sw_fence_await_dma_fence()`, and `i915_sw_fence_await_reservation()`.
- Internal wake paths include `i915_sw_fence_wake()`, dma-fence callback wakeups, timer timeout wakeups, and optional DAG checking/debug object hooks.

## Control flow
A fence starts with `pending = 1`. Awaiting another software or dma fence increments pending and registers a wait entry/callback. Committing completes the initial pending count; when the count reaches zero, the notifier receives `FENCE_COMPLETE`. If it returns `NOTIFY_DONE`, all waiters are woken without unbounded recursion by moving nested fence waiters into continuation lists. The fence then transitions to done (`pending = -1`), debug state is destroyed, and the notifier receives `FENCE_FREE`.

DMA-fence waits attach callbacks and optionally arm a timer. On dma completion or timeout, the software fence records the dma error or `-ETIMEDOUT` once and completes. Reservation waits iterate all relevant fences under `dma_resv_iter`.

## State and persistence
`struct i915_sw_fence` stores a waitqueue, notifier callback, optional debug flags, atomic pending count, and first error. Dynamically allocated wait entries/callbacks persist until their signaler completes. Timer callbacks hold dma-fence references and release them through irq work.

## Dependencies and integration points
Depends on waitqueues, dma-fence, dma-resv, timers, irq work, debug objects, and i915 selftests. Used heavily by `i915_request` submit/semaphore fences, fenced work, HuC waits, and other internal dependency chains.

## Risks
Correctness depends on pending-count transitions, acyclic software-fence graphs, callback lifetime, and wake continuation handling. Adding awaits after a fence is signaled is rejected. Timeout callbacks and dma callbacks race through `xchg()` to avoid double completion. Error propagation is first-error-wins.

## Test signals
Selftests under `selftests/lib_sw_fence.c` and `selftests/i915_sw_fence.c`, DAG-checking builds, debug-object validation, dma-fence timeout tests, reservation-object wait tests, and request submission dependency stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.h

## Purpose
Declares the i915 software fence primitive and its APIs for internal asynchronous dependency tracking.

## Important APIs, types, and functions
- `enum i915_sw_fence_notify` distinguishes `FENCE_COMPLETE` and `FENCE_FREE`.
- `i915_sw_fence_notify_t` is the owner callback type.
- `struct i915_sw_fence` stores waitqueue, callback, optional DAG flags, pending count, and error.
- `struct i915_sw_dma_fence_cb` embeds a dma-fence callback plus target software fence.
- Public APIs initialize, reinitialize, commit, await software fences, await dma fences, await reservations, increment pending, complete, test signaled/done, wait synchronously, and set an error once.

## Control flow
The lockdep-aware `i915_sw_fence_init()` macro assigns a static lock class per call site. Inline tests interpret `pending <= 0` as signaled and `pending < 0` as fully done. `i915_sw_fence_wait()` blocks on the waitqueue until done.

## State and persistence
The software fence state is embedded in owner objects such as requests or fenced work. The error field persists until reinit and is copied from signalers or dma fences.

## Dependencies and integration points
Depends on dma-fence, gfp/kref/notifier/waitqueue APIs, and optional lockdep. Included by request, scheduler-related work, and fenced work modules.

## Risks
Owners must supply a non-NULL callback and must not reinitialize while waiters remain. `i915_sw_fence_set_error_once()` ignores later errors, so caller ordering determines the reported failure. Stack-allocated wait entries require the signaler to complete before the storage is invalidated.

## Test signals
Compile-time lockdep macro coverage, software-fence selftests, dma-fence callback tests, request submit/semaphore behavior, and debug-object reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.c

## Purpose
Adapts an i915 software-fence dependency chain into a dma-fence-backed work item.

## Important APIs, types, and functions
- `dma_fence_work_init()` initializes the embedded dma fence, software fence chain, work item, and ops.
- `dma_fence_work_chain()` adds a dma-fence dependency to the chain.
- Internal `fence_notify()` schedules or directly executes work when the chain completes.
- Internal `fence_work()`, `fence_complete()`, and dma fence ops handle execution, release callback, signaling, and object lifetime.

## Control flow
Callers initialize the object, chain dependencies, then commit the software fence from the header helper. When the chain completes, errors are copied to the dma fence. If no error exists, the code takes a dma-fence reference and either runs the work immediately when `DMA_FENCE_WORK_IMM` is set or queues it to `system_dfl_wq`. Work execution calls owner `ops->work()`, releases owner resources if requested, signals the dma fence, and drops the temporary reference.

## State and persistence
`struct dma_fence_work` owns a dma fence, software chain, one embedded dma-fence callback for chaining, a work item, ops pointer, and spinlock. The dma fence remains visible to external waiters until signaled and released.

## Dependencies and integration points
Depends on `i915_sw_fence`, Linux workqueues, dma-fence, and owner-provided work/release ops. Used where i915 needs asynchronous work with a standard dma-fence completion object.

## Risks
Immediate execution is only safe before publication and when no other thread can add waits. Error paths must still signal the dma fence. The release callback runs before fence signaling in `fence_complete()`, so owner lifetime rules must account for any waiter-visible state.

## Test signals
Fenced work unit tests or consumers, dependency-chain tests, immediate-vs-queued execution tests, dma-fence wait/signaling checks, and error propagation from chained fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.h

## Purpose
Declares the dma-fence work abstraction that combines a software-fence chain with executable work and a public dma fence.

## Important APIs, types, and functions
- `struct dma_fence_work_ops` provides name, work callback, and optional release callback.
- `struct dma_fence_work` embeds `struct dma_fence`, spinlock, `struct i915_sw_fence`, one dma-fence callback, work item, and ops pointer.
- `DMA_FENCE_WORK_IMM` requests immediate execution when safe.
- APIs: `dma_fence_work_init()`, `dma_fence_work_chain()`, `dma_fence_work_commit()`, and `dma_fence_work_commit_imm()`.

## Control flow
The inline commit helpers complete the software-fence chain. `commit_imm()` first sets the immediate flag only when the chain still has at most its initial pending count, then commits.

## State and persistence
The embedded dma fence is the externally observed persistent completion state. The software fence tracks internal prerequisites until commit/completion.

## Dependencies and integration points
Depends on dma-fence, spinlocks, workqueues, and `i915_sw_fence.h`. Included by modules that want fence-signaled asynchronous work without open-coding the chaining pattern.

## Risks
`commit_imm()` has strict publication requirements described in the comment. Reusing one embedded callback means the abstraction supports the intended simple chaining pattern rather than arbitrary many callbacks stored in the struct.

## Test signals
Build coverage, immediate execution tests, queued work completion, chained dependency errors, and dma-fence release lifetime validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.c

## Purpose
Registers i915 as a VGA switcheroo client and implements power-state transitions for hybrid graphics systems.

## Important APIs, types, and functions
- `i915_switcheroo_register()` and `i915_switcheroo_unregister()` wrap `vga_switcheroo_register_client()` and unregister.
- `i915_switcheroo_set_state()` powers the GPU on/off through i915 switcheroo resume/suspend paths.
- `i915_switcheroo_can_switch()` allows switching only when DRM is initialized, display state is present, and open count is zero.
- `i915_switcheroo_ops` supplies `set_gpu_state` and `can_switch`.

## Control flow
On switch-on, the code marks DRM switch power state changing, forces PCI D0 because i915 resume does not do it here, calls `i915_driver_resume_switcheroo()`, then marks power on. On switch-off, it marks changing, calls `i915_driver_suspend_switcheroo()` with a suspend message, and marks power off. Guards reject transitions before i915/display initialization.

## State and persistence
Updates `i915->drm.switch_power_state`; the actual device power/display/GEM state is managed by the driver suspend/resume helpers. Registration persists with the PCI device until unregister.

## Dependencies and integration points
Depends on Linux VGA switcheroo, PCI power management, DRM switch power states, i915 driver suspend/resume hooks, and display-device presence detection.

## Risks
`open_count` checking is intentionally racy and avoids `drm_global_mutex` due to load-path lock inversion. Switching before display initialization or while userspace has the device open can fail or disrupt users.

## Test signals
Hybrid laptop switcheroo tests, runtime suspend/resume logs, open-file switch rejection, PCI D-state changes, display reprobing after switch-on, and suspend/resume regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.h

## Purpose
Declares i915 VGA switcheroo registration helpers.

## Important APIs, types, and functions
- Forward declares `struct drm_i915_private`.
- Exports `i915_switcheroo_register()` and `i915_switcheroo_unregister()`.

## Control flow
No runtime control flow exists in the header. It exposes a narrow API to driver load/unload code.

## State and persistence
No state is stored here. Registration state is owned by VGA switcheroo and the implementation.

## Dependencies and integration points
Included by i915 driver initialization/cleanup code and implemented by `i915_switcheroo.c`.

## Risks
The include guard lacks a trailing `_H` style suffix but is internally consistent. API expansion should remain minimal because switcheroo policy is implementation-local.

## Test signals
Build coverage and successful switcheroo register/unregister during driver probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.c

## Purpose
Implements a compact radix-tree-like map from dma-fence context IDs to the latest seqno already synchronized on a timeline, allowing i915 to skip redundant fence waits.

## Important APIs, types, and functions
- Public APIs: `i915_syncmap_init()`, `i915_syncmap_is_later()`, `i915_syncmap_set()`, and `i915_syncmap_free()`.
- Internal `struct i915_syncmap` stores prefix, height, bitmap, parent pointer, and flexible array of either seqnos or child pointers.
- Helpers compute leaf/branch prefixes and indexes, allocate leaves, set seqnos/children, insert join nodes, and recursively free the tree.

## Control flow
The root pointer is treated as a cache for the most recently used leaf. Lookup first checks the cached leaf, otherwise climbs parent pointers until it finds a branch with a matching prefix, then descends toward the target leaf. Set uses the cached leaf fast path when possible; otherwise it climbs to a common ancestor, inserts a join branch where prefixes diverge, allocates missing leaves, stores the seqno, and updates the root cache. Free climbs to the true root and recursively frees bitmap-marked children.

## State and persistence
The syncmap persists per owning timeline until freed. Leaf bitmap bits distinguish valid seqno zero from unset. Parent pointers allow a single cached leaf pointer to reach the whole tree.

## Dependencies and integration points
Depends on kernel flexible-array allocation, bit operations, i915 GEM assertions, and selftests. Used by timeline synchronization code to suppress repeated waits in `i915_request_await_dma_fence()`.

## Risks
Prefix/height math is subtle, especially around 64-bit IDs and `KSYNCMAP` radix assumptions. Sequence comparison uses signed subtraction for wraparound semantics. Allocation failures propagate to request dependency setup. Incorrect root-cache updates could leak subtrees or miss synchronization history.

## Test signals
Selftests under `selftests/i915_syncmap.c`, dense and sparse context-ID insertion, high-bit context IDs, seqno wraparound comparisons, allocation-failure paths, and request dependency squashing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.h

## Purpose
Declares the opaque i915 syncmap used to remember latest synchronized fence seqnos per context.

## Important APIs, types, and functions
- Opaque `struct i915_syncmap`.
- `KSYNCMAP` defines the radix fanout as 16.
- APIs initialize, set, query, and free syncmaps.

## Control flow
No implementation control flow exists in the header. Callers pass a pointer to their root/cache pointer so the implementation can update it after lookups and inserts.

## State and persistence
The root pointer is caller-owned and is reset to NULL by init/free. Tree contents persist until freed.

## Dependencies and integration points
Depends only on Linux types. Used by timeline code and request dependency setup.

## Risks
Callers must treat the structure as opaque and must not copy root pointers without understanding ownership. `KSYNCMAP` must remain a power-of-two compatible with implementation bitmap assumptions.

## Test signals
Build coverage plus syncmap selftests and timeline dependency-squashing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.c

## Purpose
Creates and removes i915 sysfs entries for L3 parity remapping, GT sysfs, GPU error state, and engine sysfs.

## Important APIs, types, and functions
- `kdev_minor_to_i915()` maps a DRM primary device to `drm_i915_private`.
- `i915_setup_sysfs()` creates L3 parity binary attributes when supported, the `gt` kobject, GPU error sysfs, and engine sysfs.
- `i915_teardown_sysfs()` removes those resources.
- Internal `i915_l3_read()`, `i915_l3_write()`, and `l3_access_valid()` implement L3 parity remap access.

## Control flow
Setup conditionally creates `l3_parity` and `l3_parity_slice_1` binary files for platforms with L3 DPF support, then creates a `gt` sysfs directory and delegates to GPU-error and engine sysfs setup. L3 writes validate alignment/range, allocate or reuse per-slice remap storage under the GEM context lock, copy user data, and mark every GEM context's `remap_slice` bit so remapping is applied on context switch.

## State and persistence
Persistent state includes `i915->l3_parity.remap_info[slice]`, per-context `remap_slice` bits, `dev_priv->sysfs_gt`, GPU error sysfs objects, and engine sysfs entries. L3 remap state remains until driver cleanup or replacement.

## Dependencies and integration points
Depends on Linux sysfs/bin_attribute APIs, DRM device/minor plumbing, GT/RPS/RC6/engine sysfs, GPU error sysfs, L3 parity capability macros, and GEM context lists.

## Risks
L3 sysfs writes are privileged but directly affect context remapping and can leave errors propagated until a future GPU reset, noted as a TODO. Teardown removes both L3 files unconditionally, which sysfs tolerates. `gt` kobject creation failure is warning-only, so downstream sysfs code must handle missing directories.

## Test signals
Sysfs presence/absence on HAS_L3_DPF platforms, aligned and unaligned L3 read/write tests, multi-slice systems, context switch applying remap bits, GPU error sysfs operations, engine sysfs visibility, and probe/remove cleanup checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.h

## Purpose
Declares i915 sysfs setup/teardown helpers and a device-to-i915 lookup utility.

## Important APIs, types, and functions
- Forward declares `struct device` and `struct drm_i915_private`.
- Exports `kdev_minor_to_i915()`, `i915_setup_sysfs()`, and `i915_teardown_sysfs()`.

## Control flow
No runtime control flow exists in the header. It provides the setup/cleanup contract to driver initialization.

## State and persistence
No state is defined here. The implementation stores sysfs state in `drm_i915_private` and kernel sysfs objects.

## Dependencies and integration points
Included by i915 driver load/remove paths and the sysfs implementation.

## Risks
The lookup helper assumes the device has DRM minor driver data installed. Calling it on unrelated devices would produce invalid results.

## Test signals
Build coverage and probe/remove sysfs setup/teardown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_tasklet.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_tasklet.h

## Purpose
Provides small wrappers around Linux tasklet state used by i915 scheduler/submission code.

## Important APIs, types, and functions
- `tasklet_lock()` spins until `tasklet_trylock()` succeeds.
- `tasklet_is_locked()` tests `TASKLET_STATE_RUN`.
- `__tasklet_disable_sync_once()` increments the disable count and waits for a running tasklet only on the first disable.
- `__tasklet_is_enabled()`, `__tasklet_enable()`, and `__tasklet_is_scheduled()` expose count and scheduled-state checks.

## Control flow
The helpers are inline. Locking uses CPU relax in a spin loop. Disable/enable operate on the tasklet count directly and rely on the kernel tasklet state machine.

## State and persistence
No state is owned by this header. It reads and mutates `struct tasklet_struct` state bits and count in caller-owned tasklets.

## Dependencies and integration points
Depends on Linux interrupt/tasklet APIs. Used by i915 scheduler-engine helpers and backend tasklet control.

## Risks
These are low-level wrappers around internal tasklet fields. Mispaired disable/enable or spinning with inappropriate locks held can deadlock or starve softirq progress.

## Test signals
Lockdep, tasklet submission stress, scheduler active-lock tests, and softirq recursion/preemption tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_tasklet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.c

## Purpose
Implements small timer utilities that use `expires == 0` as i915's canceled/inactive sentinel.

## Important APIs, types, and functions
- `cancel_timer()` deletes an active timer and writes `expires = 0`.
- `set_timer_ms()` arms a timer in milliseconds or cancels it for timeout zero.

## Control flow
`cancel_timer()` first checks `timer_active()` from the header, then calls `timer_delete()` and clears `expires`. `set_timer_ms()` converts milliseconds to jiffies, uses a compiler barrier before reading volatile `jiffies`, and calls `mod_timer()` with a nonzero expiration so zero remains reserved for canceled state.

## State and persistence
The only state touched is the caller-owned `struct timer_list`, especially `expires`.

## Dependencies and integration points
Depends on Linux jiffies/timer APIs and `i915_timer_util.h`. Intended for i915 code that wants cheap active/expired checks separate from generic timer pending state.

## Risks
The helpers assume no other code uses `expires == 0` differently for the same timer. `timer_delete()` does not guarantee callback synchronization the way shutdown/sync variants do; callers must choose the right lifetime protocol.

## Test signals
Timer unit tests, timeout-zero cancellation checks, expired-vs-pending state checks, and races around cancellation during callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.h

## Purpose
Declares i915 timer helpers and inline state predicates based on the timer expiration field.

## Important APIs, types, and functions
- `cancel_timer()` and `set_timer_ms()` are implemented in the C file.
- `timer_active()` returns whether `expires` is nonzero.
- `timer_expired()` returns active but not currently pending.

## Control flow
Inline predicates use `READ_ONCE()` for `expires` and generic `timer_pending()` for pending state.

## State and persistence
No state is owned here. Callers opt into `expires = 0` as inactive state.

## Dependencies and integration points
Depends on Linux timers and `READ_ONCE`. Used by i915 timeout/watchdog-style code that needs active/expired predicates.

## Risks
Directly interpreting `expires` is more specialized than generic timer APIs. Callers must keep all manipulation through compatible helpers to avoid stale active state.

## Test signals
Build coverage and timer behavior tests covering active, pending, expired, canceled, and rearmed states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace.h

## Purpose
Defines Linux tracepoints for i915 GEM object lifecycle, VMA binding, eviction, request lifecycle/waits, optional low-level request and context events, PPGTT lifetime, and GEM context lifetime.

## Important APIs, types, and functions
- Trace events include `i915_gem_object_create`, `i915_gem_shrink`, `i915_vma_bind`, `i915_vma_unbind`, object pwrite/pread/fault, object clflush/destroy, eviction events, `i915_request_queue`, request add/retire/wait begin/end, PPGTT create/release, and context create/free.
- Low-level tracepoints gated by `CONFIG_DRM_I915_LOW_LEVEL_TRACEPOINTS` include request GuC submit/submit/execute/in/out and many Intel context state events.
- When low-level tracing is disabled, inline no-op functions preserve call sites.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` configure trace header generation.

## Control flow
Tracepoint macros describe argument capture and formatted print output. Request tracepoints record device index, engine class/instance, fence context/seqno, tail, flags, priority, port, or completion state. Context tracepoints record GuC ID, pin count, scheduler state, and GuC priority.

## State and persistence
Tracepoints do not store persistent driver state beyond transient ftrace/perf buffers. They observe live GEM, VM, request, and context fields at trace call time.

## Dependencies and integration points
Depends on Linux tracepoint infrastructure, DRM device types, Intel engine helpers, and i915 request/context/GEM structures. Used by request code, GEM memory management, VM code, GuC/execlists backend instrumentation, and debugging tools.

## Risks
Tracepoint field layouts are consumed by tooling, so changing event names or field names can break diagnostics. Capturing pointer fields and racy request completion state is acceptable for tracing but should not be interpreted as synchronization. Low-level no-op stubs must match real tracepoint signatures.

## Test signals
Builds with tracing on/off, `trace-cmd`/ftrace event availability, request lifecycle traces matching add/submit/execute/retire ordering, GEM object/VM leak debugging, and low-level GuC/context trace validation when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace_points.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace_points.c

## Purpose
Instantiates the i915 tracepoints declared in `i915_trace.h`.

## Important APIs, types, and functions
- Defines `CREATE_TRACE_POINTS` before including `i915_trace.h` when not under sparse checker mode.
- Includes `i915_drv.h` for required i915 types.

## Control flow
No ordinary runtime control flow exists. The compile unit causes tracepoint definitions to be emitted exactly once for the trace system.

## State and persistence
Tracepoint static metadata and registration storage are generated by the tracepoint infrastructure.

## Dependencies and integration points
Depends on Linux tracepoint generation rules and the `TRACE_INCLUDE_*` settings in `i915_trace.h`. Integrated by the i915 build so trace events link correctly.

## Risks
Including `i915_trace.h` with `CREATE_TRACE_POINTS` in more than one compilation unit would duplicate definitions. Omitting this file would leave trace call sites unresolved or unavailable.

## Test signals
Successful link, ftrace event registration under `/sys/kernel/tracing/events/i915`, and builds under sparse/checker conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace_points.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.c

## Purpose
Implements a TTM resource manager backed by the Linux GPU buddy allocator for i915 memory regions, including CPU-visible memory accounting and reserved ranges.

## Important APIs, types, and functions
- TTM manager callbacks: `i915_ttm_buddy_man_alloc()`, `i915_ttm_buddy_man_free()`, `i915_ttm_buddy_man_intersects()`, `i915_ttm_buddy_man_compatible()`, and `i915_ttm_buddy_man_debug()`.
- Public APIs: `i915_ttm_buddy_man_init()`, `i915_ttm_buddy_man_fini()`, `i915_ttm_buddy_man_reserve()`, `i915_ttm_buddy_man_visible_size()`, `i915_ttm_buddy_man_avail()`, and selftest-only `i915_ttm_buddy_man_force_visible_size()`.
- Internal manager state tracks `ttm_resource_manager`, `gpu_buddy`, reserved blocks, lock, visible size/availability/reserved pages, and default page size.

## Control flow
Allocation creates an `i915_ttm_buddy_resource`, translates TTM placement flags into buddy flags, computes minimum page size from manager default or BO alignment, checks requested range/visible availability, allocates buddy blocks, computes how many allocated pages fall in the CPU-visible aperture, updates visible availability, and returns the TTM resource. Free returns blocks to the buddy allocator, restores visible availability, finalizes the TTM resource, and frees the wrapper.

Intersection/compatibility callbacks compare a resource's blocks with a requested placement range, with fast paths for "any placement" and "CPU-visible only" checks. Init allocates the manager, initializes the buddy allocator with region size/chunk size, registers it with TTM, and marks it used. Fini marks it unused, evicts all resources, unregisters it, frees reserved blocks, verifies visible accounting, cleans up TTM, and frees the manager.

## State and persistence
Persistent manager state is registered in the TTM device per memory type. Each allocation persists as `i915_ttm_buddy_resource` with a block list, flags, used visible page count, and buddy pointer. Reserved blocks remain on the manager until fini/deallocation.

## Dependencies and integration points
Depends on Linux `gpu_buddy`, DRM buddy debug printing, TTM resource manager APIs, TTM BO placement flags, and i915 GEM assertions. Used by i915 TTM-backed memory regions and scatterlist construction.

## Risks
Visible memory accounting is critical for small-BAR systems. Range allocations must respect TTM `fpfn/lpfn`, alignment, top-down/contiguous flags, and chunk-size constraints. `i915_ttm_buddy_man_reserve()` updates visible accounting even if allocation fails after the visible range calculation, which should be checked carefully when modifying.

## Test signals
TTM memory allocation/eviction tests, small-BAR visible placement tests, contiguous and top-down allocation tests, reserved-range tests, debugfs output, selftests forcing visible size, and teardown verifying visible availability equals visible size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.h

## Purpose
Declares i915's TTM buddy resource wrapper and manager APIs.

## Important APIs, types, and functions
- `struct i915_ttm_buddy_resource` extends `struct ttm_resource` with buddy block list, allocation flags, visible-page usage, and buddy allocator pointer.
- `to_ttm_buddy_resource()` upcasts from TTM resource.
- APIs initialize/finalize a manager, reserve address ranges, query visible size, query total/visible availability, and force visible size in selftests.

## Control flow
The header is mostly declarative. `to_ttm_buddy_resource()` uses `container_of()` and assumes the passed resource was allocated by this manager.

## State and persistence
The structure defines persistent per-allocation state until the TTM resource is freed. Manager state is opaque to callers.

## Dependencies and integration points
Depends on Linux list/types and TTM resource APIs. Used by TTM memory-region setup, scatterlist construction, and tests.

## Risks
Passing a resource from another TTM manager to `to_ttm_buddy_resource()` is invalid. The `used_visible_size` unit is pages, while many public API sizes are bytes or pages depending on function, so callers must respect documented units.

## Test signals
Build coverage, TTM allocation/free tests, visible availability queries, and selftest-only visible-size manipulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.c

## Purpose
Implements generic parsing for chained i915 userspace extension structures.

## Important APIs, types, and functions
- `i915_user_extensions()` walks a user pointer chain and dispatches extension handlers from a caller-supplied table.
- Uses `check_user_mbz()` for reserved flags/fields, `get_user()` for name and next pointer, `array_index_nospec()` for Spectre-safe table indexing, and `u64_to_user_ptr()` for chaining.

## Control flow
The parser loops while the user extension pointer is non-NULL. It enforces a stack-depth/chain limit of 512, validates `flags` and all reserved fields are zero, reads the extension name, dispatches the matching handler if the name is in range and present, returns handler errors, reads and validates `next_extension`, and advances to the next user pointer.

## State and persistence
No driver state is stored by the parser. Handler callbacks may mutate caller-provided `data`. The only persistent effect is whatever accepted extensions configure in their caller context.

## Dependencies and integration points
Depends on i915 UAPI `struct i915_user_extension`, Linux user access, nospec helpers, signal header inclusion, and `i915_utils.h`. Used by ioctl implementations that accept extensible chained user structures.

## Risks
The ABI requires all reserved fields to be zero for forward compatibility. Invalid pointers return `-EFAULT`; unknown or unsupported names return `-EINVAL`. Very long chains return `-E2BIG`. Callback tables must match UAPI extension IDs exactly.

## Test signals
Ioctl tests with valid chains, unknown names, unsupported holes, nonzero reserved fields, invalid user pointers, pointer-width overflow, chain-depth limit, and Spectre/nospec static analysis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.h

## Purpose
Declares the generic i915 user-extension chain parser and callback type.

## Important APIs, types, and functions
- Forward declares `struct i915_user_extension`.
- `i915_user_extension_fn` callback receives the user extension pointer and caller data.
- `i915_user_extensions()` dispatches a chain through a callback table.

## Control flow
No implementation control flow exists in the header. It defines the callback contract for C files that parse UAPI extension chains.

## State and persistence
No state is stored here.

## Dependencies and integration points
Included by ioctl implementation files and implemented by `i915_user_extensions.c`.

## Risks
Callbacks receive user pointers and must perform their own safe copies for extension-specific payloads. Table count must correspond to the highest accepted UAPI name plus one.

## Test signals
Build coverage and ioctl extension parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_user_extensions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.c

## Purpose
Implements small i915 utility functions for CI tainting, VT-d/guest detection, and Meteor Lake direct stolen-memory access policy.

## Important APIs, types, and functions
- `add_taint_for_CI()` logs a CI taint reason and calls `__add_taint_for_CI()`.
- `i915_vtd_active()` returns true when the device is IOMMU mapped or the driver runs as a guest.
- `i915_direct_stolen_access()` implements Wa_22018444074 policy for direct GSM/DSM access on Meteor Lake when firmware permits it and the driver is not in a guest.

## Control flow
VT-d detection first asks the device IOMMU API, then treats guests as protected by the host. Direct stolen access checks platform, guest status, and `MTL_PCODE_STOLEN_ACCESS` register value through uncore.

## State and persistence
No local persistent state is stored. CI taint affects global kernel taint state. Direct-access decisions reflect current platform and firmware register state.

## Dependencies and integration points
Depends on DRM logging, device IOMMU APIs, i915 platform detection, uncore register access, and register definitions from `i915_reg.h`. Used by memory-management and CI/error-handling paths.

## Risks
Guest detection is architecture-limited; non-x86 returns false. Incorrect direct stolen-memory access policy can hang MTL systems or break guests that cannot access GSM/DSM directly. CI tainting intentionally marks the kernel as unreliable for automated testing.

## Test signals
CI taint log/taint-state checks, IOMMU-on/off boot tests, guest VM tests, MTL firmware register validation, and stolen-memory access tests on MTL and non-MTL systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.h

## Purpose
Declares common i915 utility macros and helpers used across the driver.

## Important APIs, types, and functions
- Diagnostic/logging helpers: `MISSING_CASE()`, `i915_probe_error()`, `add_taint_for_CI()`, and `__add_taint_for_CI()`.
- Generic helpers: `fetch_and_zero()`, `check_user_mbz()`, `__mask_next_bit()`, and `is_power_of_2_u64()`.
- Environment/platform helpers: `i915_run_as_guest()`, `i915_vtd_active()`, and `i915_direct_stolen_access()`.

## Control flow
Most helpers are macros/inlines. `check_user_mbz()` safely reads a user field and requires zero. `i915_run_as_guest()` uses x86 hypervisor detection when available and returns false on unsupported architectures.

## State and persistence
No local state is stored. Some helpers mutate pointed-to variables (`fetch_and_zero`, `__mask_next_bit`) or global kernel taint state.

## Dependencies and integration points
Depends on Linux overflow, scheduler, string, workqueue, sched clock, user access through callers, optional x86 hypervisor APIs, and DRM/i915 private declarations. Included broadly across i915.

## Risks
Macros evaluate pointer arguments in ways callers must understand. `fetch_and_zero()` is not atomic. `check_user_mbz()` must only be used with user pointers. Guest detection fallback can be conservative only on x86.

## Test signals
Build coverage, sparse/user-pointer checking, ioctl reserved-field tests, taint-state tests, and platform/guest detection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.c

## Purpose
Implements Intel GVT-g vGPU detection, capability queries, display-ready notification, and GGTT address-space ballooning/deballooning for guest drivers.

## Important APIs, types, and functions
- `intel_vgpu_detect()` maps the PVINFO MMIO page, validates magic/version, records capabilities, initializes vGPU state, and logs detection.
- `intel_vgpu_register()` writes display-ready state for active vGPUs.
- Capability queries: `intel_vgpu_active()`, `intel_vgpu_has_full_ppgtt()`, `intel_vgpu_has_hwsp_emulation()`, and `intel_vgpu_has_huge_gtt()`.
- Ballooning APIs: `intel_vgt_balloon()` and `intel_vgt_deballoon()`.
- Internal helpers reserve/deallocate unavailable GGTT ranges with `vgt_balloon_space()` and `vgt_deballoon_space()`.

## Control flow
Detection runs early before normal uncore MMIO setup, maps the PCI BAR range containing PVINFO, rejects older graphics versions, checks `VGT_MAGIC` and interface version, reads caps, and marks vGPU active. Ballooning reads mappable and unmappable guest-owned graphics memory ranges from PVINFO registers, validates them against GGTT mappable and total boundaries, then reserves all gaps before, between, and after those ranges. On partial failure it rolls back earlier reservations.

## State and persistence
Persistent state includes `dev_priv->vgpu.active`, capability bits, vGPU lock, and a static `_balloon_info_` containing up to four `drm_mm_node` reservations. Ballooned GGTT nodes reduce `ggtt->vm.reserved` until deballooned.

## Dependencies and integration points
Depends on PCI BAR mapping, DRM logging, PVINFO structures/register macros, i915 GGTT reservation APIs, uncore register access, and display-ready integration after modeset. Used during driver initialization and cleanup in virtualized environments.

## Risks
Balloon configuration from the host must be valid; invalid ranges are rejected. Static balloon info assumes one active relevant vGPU instance in this driver context. Reservation/deballoon accounting must stay balanced or GGTT space can leak. Detection cannot use normal uncore access because it runs before those mappings exist.

## Test signals
GVT-g guest boot detection logs, capability-dependent paths, display-ready notification observed by host, valid/invalid balloon configuration tests, GGTT reservation accounting, unload deballoon cleanup, and non-vGPU bare-metal no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.h

## Purpose
Declares i915 vGPU detection, capability, registration, and GGTT ballooning APIs.

## Important APIs, types, and functions
- Forward declares `struct drm_i915_private` and `struct i915_ggtt`.
- Exports `intel_vgpu_detect()`, `intel_vgpu_active()`, `intel_vgpu_register()`, capability query helpers, `intel_vgt_balloon()`, and `intel_vgt_deballoon()`.

## Control flow
No implementation control flow exists in the header. It exposes the vGPU contract to initialization, GGTT setup, and capability users.

## State and persistence
No state is defined here; state lives in `drm_i915_private->vgpu` and implementation balloon nodes.

## Dependencies and integration points
Included by driver probe, GGTT initialization, and code paths that adapt behavior for GVT-g guests.

## Risks
Capability helpers are meaningful only after `intel_vgpu_detect()` has run. Balloon/deballoon must be paired around GGTT lifetime.

## Test signals
Build coverage, guest/bare-metal initialization tests, and GGTT balloon/deballoon integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vgpu.h -->
