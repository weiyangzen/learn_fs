# sources/distributed-fs/ceph-client/kernel/trace/trace_clock.c

## Purpose
`trace_clock.c` implements trace timestamp providers with different precision, ordering, and overhead tradeoffs: CPU-local, medium/global-ish, jiffies, globally monotonic, and pure counter clocks.

## Important APIs, types, and functions
Exported functions are `trace_clock_local()`, `trace_clock()`, `trace_clock_jiffies()`, `trace_clock_global()`, and `trace_clock_counter()`. Important state includes `trace_clock_struct`, which stores `prev_time` and an `arch_spinlock_t` in the same cache line, and the atomic `trace_counter`.

## Control flow
`trace_clock_local()` disables preemption and reads `sched_clock()`. `trace_clock()` returns `local_clock()`, accepting small inter-CPU jitter. `trace_clock_jiffies()` converts jiffies since `INITIAL_JIFFIES`. `trace_clock_global()` disables local IRQs, reads the previous global timestamp with barriers, reads `sched_clock_cpu()`, clamps backward movement, and tries to update `prev_time` under an arch spin trylock; in NMI context it avoids locking and returns the clamped time. `trace_clock_counter()` atomically increments and returns a strict ordering counter.

## State and persistence behavior
The global clock persists the last returned timestamp in static memory. The counter clock persists a monotonically increasing `atomic64_t`. Other clocks store no state in this file.

## Dependencies and integration points
The file depends on scheduler clocks, jiffies, spinlocks, IRQ state helpers, per-CPU CPU IDs, NMI detection, atomics, and `<linux/trace_clock.h>`. Tracers and event code select these clocks through trace array clock configuration.

## Risks
The local and medium clocks are intentionally not fully coherent across CPUs. The jiffies clock has a documented small 32-bit safety window. The global clock avoids lockups by using trylock and bypassing locking in NMI, so it is best-effort globally ordered rather than a hard serialization in every context.

## Test signals
Switch trace clocks via tracefs and verify event timestamp monotonicity expectations per clock. Stress with cross-CPU events, idle transitions, NMI-heavy paths, and counter-clock ordering checks.
