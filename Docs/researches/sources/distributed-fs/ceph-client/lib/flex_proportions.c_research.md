# sources/distributed-fs/ceph-client/lib/flex_proportions.c

## Purpose
Implements floating proportions with exponential aging and lazy per-type period reflection. Callers can maintain a global event denominator and local per-type numerators, then query smoothed proportions without iterating all event types every period.

## Important APIs, Types, and Functions
Global APIs are `fprop_global_init()`, `fprop_global_destroy()`, and `fprop_new_period()`. Per-CPU local APIs are `fprop_local_init_percpu()`, `fprop_local_destroy_percpu()`, `__fprop_add_percpu()`, `fprop_fraction_percpu()`, and `__fprop_add_percpu_max()`. Internal `fprop_reflect_period_percpu()` lazily ages one local counter to the current global period. `PROP_BATCH` sizes percpu counter batching by CPU count.

## Control Flow
Global initialization starts the denominator at one to avoid zero-event periods and initializes a seqcount. `fprop_new_period()` sums global events, subtracts the aged-away portion, increments the period under seqcount write protection, and returns whether further aging matters. Local add paths first reflect period changes for that local counter, then add to local and global percpu counters. Fraction queries read under seqcount retry, reflect local aging, read positive local/global counters, and clamp denominator so the fraction remains valid. Max-add computes whether adding `nr` would exceed a configured fraction and truncates or skips the add.

## State and Persistence
State is caller-owned in `struct fprop_global` and `struct fprop_local_percpu`: percpu counters, period numbers, seqcount, and local raw spinlock. No global state or allocation beyond percpu counter initialization is owned here.

## Dependencies and Integration Points
Depends on `linux/flex_proportions.h`, percpu counters, seqcount, raw spinlocks, interrupt save/restore, and 64-bit division helpers. It is used by subsystems that need throttling or proportional accounting with aging, such as writeback-style balancing.

## Risks
Callers must serialize `fprop_new_period()` externally as documented. PerCPU counter approximation can temporarily make numerator exceed denominator; the function clamps output but callers should expect approximate fractions. Period jumps of at least `BITS_PER_LONG` zero local counters. Max-add arithmetic must avoid overflow for large `nr`/denominator combinations.

## Test Signals
Test initialization/destruction, period advancement with no events and many events, lazy local aging, fraction normalization, max-fraction saturation, concurrent readers during period changes, and large period jumps. Integration tests should validate smooth proportional throttling behavior over time.
