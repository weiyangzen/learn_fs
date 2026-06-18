# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_execlists_submission.c

## Purpose
This file implements the legacy logical-ring/execlists submission backend for Gen8+ i915 engines. It creates and pins logical-ring contexts, queues requests by priority, submits context descriptors to ELSP/ELSQ ports, processes context status buffer events, supports preemption and timeslicing, handles virtual engines for load balancing, and participates in reset, capture, PM, IRQ, and busyness accounting.

## Important APIs, Types, and Functions
The public entry points are `intel_execlists_submission_setup()`, `intel_execlists_show_requests()`, and `intel_execlists_dump_active_requests()`. The key internal type is `struct virtual_engine`, which embeds an `intel_engine_cs`, an owning `intel_context`, a pending request, per-physical-engine RB nodes, and sibling engine pointers.

Core scheduling functions include `execlists_submit_request()`, `queue_request()`, `submit_queue()`, `kick_execlists()`, `execlists_dequeue()`, `execlists_submit_ports()`, `execlists_update_context()`, and `write_desc()`. CSB processing is handled by `process_csb()`, `csb_read()`, `gen8_csb_parse()`, `gen12_csb_parse()`, and `xehp_csb_parse()`. Context lifecycle and request allocation use `execlists_context_ops`, `execlists_context_pre_pin()`, `execlists_context_pin()`, `execlists_request_alloc()`, and `emit_pdps()`. Reset/capture paths include `execlists_reset_prepare()`, `execlists_reset_rewind()`, `execlists_reset_cancel()`, `execlists_reset_finish()`, `execlists_capture()`, and `execlists_hold()/unhold()`. Virtual submission uses `execlists_create_virtual()`, `virtual_submit_request()`, and `virtual_submission_tasklet()`.

## Control Flow
Setup installs vfuncs, IRQ masks, tasklet callbacks, timers, CSB pointers, submit registers, context tags, and engine cleanup hooks. A request submitted to an execlists engine is placed on a priority queue or hold list under the scheduler lock. If its priority exceeds the queue hint, the submission tasklet is kicked.

The tasklet first drains CSB events, promoting pending ports to inflight ports or scheduling out completed contexts. It handles preemption timeout and CS error interrupts, then dequeues new work if no submission is pending. `execlists_dequeue()` compares active contexts with queued and virtual work, may unwind incomplete requests for preemption or expired timeslice, merges adjacent same-context requests into one tail update, fills up to two ports, calls schedule-in accounting, sets preempt timers, and writes descriptors to ELSP/ELSQ. IRQ handling records CS errors, semaphore-yield requests, context-switch interrupts, and user interrupts for breadcrumbs.

Reset flow disables the tasklet, pauses the ring through the HWSP preempt semaphore, stops the command streamer, records the active CCID, drains CSB events, rewinds or cancels requests, resets CSB pointers, and re-enables the tasklet so queued work can replay.

## State and Persistence Behavior
Persistent engine state lives in `engine->execlists`: CSB head/write/status state, active/inflight/pending port arrays, virtual-engine RB tree, timers, error bits, context tag allocation, and preemption target. Request state moves between priority queues, executing request lists, hold lists, pending/inflight port references, and virtual-engine request slots. Runtime PM references and forcewake are taken on schedule-in and released on final schedule-out. Context image state is rewritten during submission, reset, and pre-pin.

## Dependencies and Integration Points
The backend integrates with logical-ring context code (`intel_lrc`), request/timeline/fence handling, `i915_sched_engine`, breadcrumbs, GT PM, uncore MMIO, MOCS, workarounds, reset machinery, i915 error capture, GVT notifiers, command emission helpers in `gen8_engine_cs`, virtual engine UABI, PMU stats, and selftests.

## Risks
The largest risks are concurrency and hardware ordering. CSB events can be stale or reordered, so reads use barriers, HWSP poisoning, MMIO fallback, and cacheline flushes. Port state is visible from tasklets, reset code, RCU readers, and retirement; reference handling mistakes can cause use-after-free or leaked requests. Preemption and timeslicing unwind requests while the GPU may still be executing them. Incorrect context-tail or force-restore handling can replay stale batches or skip dependencies. Virtual engines rely on stable sibling compatibility and careful request migration between physical engines.

## Test Signals
Signals include passing `selftest_execlists`, GPU hang/reset recovery tests, preemption and timeslice tests, semaphore wait/yield behavior, virtual-engine load balancing, request cancellation, suspend/resume, PMU busyness accuracy, no CSB invalid-event resets under load, stable breadcrumbs/user interrupts, and lockdep/KASAN-clean operation during reset and retirement stress.
