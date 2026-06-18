# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_atomic.c

## Purpose
This file defines reusable atomic-context phases for selftests that need to run code under preemption, softirq, or hardirq-disabled conditions.

## Important APIs, Types, And Functions
The exported object is `igt_atomic_phases[]`, an array of `struct igt_atomic_section`. Local helpers pair begin/end functions for `preempt_disable`/`preempt_enable`, `local_bh_disable`/`local_bh_enable`, and `local_irq_disable`/`local_irq_enable`.

## Control Flow
Consumers iterate `igt_atomic_phases` until the sentinel empty record. For each phase they call `critical_section_begin()`, execute the code under test, then call `critical_section_end()`.

## State And Persistence
The file stores only a constant table. Runtime state is the CPU’s preemption, bottom-half, or interrupt enable state while a phase is active.

## Dependencies And Integration Points
It depends on Linux preempt, bottom-half, and irq flag APIs, and on the declaration in `igt_atomic.h`. It is a helper for low-level selftests that validate behavior in atomic contexts.

## Risks
Callers must always pair begin/end or the CPU context will remain altered. Tests must avoid sleeping in phases where sleep is illegal.

## Test Signals
This file produces no direct test result; downstream tests report whether their operation is safe across these atomic phases.
