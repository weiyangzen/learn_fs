# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_submission.c

## Purpose

This file implements the GuC-backed i915 command submission backend. It replaces execlists-style scheduling with GuC context registration, GuC ID management, H2G submit/schedule-control messages, G2H completion/reset handlers, GuC-owned busyness accounting, TLB invalidation, virtual-engine support, and multi-LRC parallel submission. The large top-level comment is accurate: the driver owns LRC tail updates, context lifecycle, and host-side state consistency while GuC owns firmware scheduling once contexts are registered and enabled.

## Important APIs, Types, And Functions

Important exported entry points are `intel_guc_submission_init_early()`, `intel_guc_submission_init()`, `intel_guc_submission_setup()`, `intel_guc_submission_enable()`, `intel_guc_submission_disable()`, `intel_guc_submission_fini()`, reset/cancel helpers, busyness park/unpark, G2H handlers, debug printers, and `intel_guc_virtual_engine_has_heartbeat()`. Internal state is centered on `struct intel_guc::submission_state`, `context_lookup` xarray, `guc_id` refs on `struct intel_context`, `ce->guc_state.sched_state`, and the single shared `i915_sched_engine` tasklet.

The scheduling-state bit helpers manage pending enable/disable, registered, destroyed, banned, closed, deregister-to-register wait, and a blocked counter. `guc_request_alloc()` is the key request-preparation hook: it reserves GuC request space, emits cache/TLB invalidation, initializes GuC context state, cancels delayed schedule-disable work, pins or steals a GuC ID, registers the context if needed, and attaches request submit fences when disable or deregister G2H replies are pending.

Submission flows through `guc_submit_request()`, `queue_request()`, `guc_submission_tasklet()`, `guc_dequeue_one_context()`, `try_context_registration()`, `guc_wq_item_append()` for multi-LRC, `guc_set_lrc_tail()` for normal contexts, and `guc_add_request()`. Context registration supports both pre-1.0 GuC submission descriptors in a shared LRC descriptor pool and v1.0+ KLV-style registration structures. `guc_context_policy_init_v70()` and the v69 descriptor policy code push priority, timeslice, preemption timeout, forced preempt-to-idle, and SLPC context-frequency metadata.

## Control Flow

Early init creates locks, lists, ID allocators, workers, timestamp work, default schedule-disable delay, GuC ID limits, and support/selection booleans. `intel_guc_submission_init()` allocates the v69 descriptor pool when required, initializes TLB invalidation lookup state, allocates the multi-LRC GuC ID bitmap, computes timestamp worker cadence, and marks submission initialized. `intel_guc_submission_setup()` installs GuC engine vfuncs, a shared virtual sched engine, breadcrumbs, IRQ handlers, request hooks, reset hooks, and RCS-specific emit overrides.

Enable routes Gen12 semaphore interrupts to GuC, initializes pinned kernel contexts, starts GuC usage stats, and programs global scheduling policy for newer firmware. Disable cancels busyness sampling and routes semaphores back to the host. Runtime request submission tries a direct H2G path when the context is already mapped, the queue is empty, submission is enabled, and no stalled request exists; otherwise it queues work on the tasklet. Stalls on full CT/work queues are persisted in `guc->stalled_request` plus `submission_stall_reason` and retried by the tasklet.

Reset prepare disables submission, interrupts, CT receive handling, heartbeats, and destroyed-context work, then scrubs outstanding G2H effects so lost replies cannot leak GuC IDs or leave fences blocked. Reset replays pinned parent contexts, resets guilty requests, unwinds incomplete requests back to the priority queue, destroys the context lookup, and wakes TLB waiters. Reset finish clears unexpected outstanding G2H count, restores global policies, reenables submission, unparks heartbeats, and wakes invalidation waiters.

## State, Persistence, And Concurrency

The driver persists GuC context identity in an IDA for normal contexts and a reserved bitmap region for contiguous multi-LRC parent/children. Unpinned normal contexts with zero request refs are added to a reusable list and may have their GuC ID stolen. The xarray maps active GuC IDs to contexts and doubles as a registration-present test. Destroyed contexts are queued to a worker because deregistration can need GT PM and cannot always run in atomic context.

`ce->guc_state.lock`, `guc->submission_state.lock`, and `sched_engine->lock` protect distinct domains, with documented lock ordering. The blocked sw fence prevents resubmission while schedule-disable or deregistration is in flight. Outstanding G2H replies are counted in `guc->outstanding_submission_g2h` and waited on by suspend/idle paths. Busyness state extends GuC 32-bit GT timestamps into monotonic 64-bit accounting with a delayed worker and reset-aware rollback.

## Dependencies And Integration Points

The file integrates with i915 LRC/ring helpers, scheduler priority lists, GT PM and reset, GuC CT/H2G APIs, GuC ADS, capture, breadcrumbs, engine IRQs, MOCS, SLPC policy fields, runtime PM, xarray/IDA/bitmap allocators, and debug/error capture. It is called from the broader `intel_uc.c` load/reset/suspend path after GuC firmware and CT communication are ready.

## Risks And Test Signals

Risk is concentrated in races around lost G2H replies, context close versus request allocation, GuC ID stealing, schedule-disable fences, reset while CT is full, and multi-LRC work-queue wrap/handshake correctness. The state bits are compact and lock-sensitive, so missing a lock or decrement can deadlock submissions or leak IDs. TLB invalidation is in reclaim-sensitive paths and has serial-slot fallback under memory pressure. Test signals include GuC submission selftests included at file end, hangcheck and multi-LRC selftests, suspend/resume, GT reset and wedged paths, debugfs context dumps, PMU engine busyness, CT timeout logs, no stuck `outstanding_submission_g2h`, and successful virtual/parallel engine workloads.
