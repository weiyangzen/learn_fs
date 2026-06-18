<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_stats.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_stats.h

## Purpose
`intel_engine_stats.h` provides inline execlists engine busyness accounting helpers for context-in/context-out transitions.

## Important APIs, Types, and Functions
The two helpers are `intel_engine_context_in(struct intel_engine_cs *engine)` and `intel_engine_context_out(struct intel_engine_cs *engine)`. Both operate on `engine->stats.execlists`.

## Control Flow
`intel_engine_context_in()` increments nested active count if already active; otherwise it disables local IRQs, begins a seqcount write, records `ktime_get()` as the start time, increments active, ends the seqcount, restores IRQs, and asserts active is nonzero. `intel_engine_context_out()` decrements nested active count if more than one context is active; otherwise it disables local IRQs, begins a seqcount write, decrements active, adds elapsed time since `start` to `total`, ends the seqcount, and restores IRQs.

## State and Persistence
Persistent state is `engine->stats.execlists.active`, `start`, `total`, and the seqcount lock. The total accumulated busy time feeds PMU/stat readers and engine diagnostics.

## Dependencies and Integration Points
The header depends on atomics, ktime, seqlock, GEM assertions, and `intel_engine.h`. It is used by execlists context switch paths and read by PMU or busy-time helpers that need consistent snapshots from hardirq-capable readers.

## Risks and Edge Cases
The writer is serialized by the submission backend, but readers may run in hardirq, so seqcount and local IRQ disabling are required. Active underflow is fatal. Nested active counts must match context in/out events or total busy time will be inflated or lost.

## Test Signals
Signals include PMU busy-time tests, nested context switch accounting, active underflow debug assertions, hardirq reader consistency, and engine dump runtime values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_stats.h -->
