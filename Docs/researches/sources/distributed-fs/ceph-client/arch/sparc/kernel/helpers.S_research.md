# sources/distributed-fs/ceph-client/arch/sparc/kernel/helpers.S

## Purpose
`helpers.S` contains small sparc64 assembly helpers for register-window flushing, stack trace preparation, and hardware CPU ID retrieval.

## Important APIs, Types, and Functions
Exports include `__flushw_user`, `stack_trace_flush`, `real_hard_smp_processor_id`, and, under SMP, `hard_smp_processor_id`. `__flushw_user` is exported to modules.

## Control Flow and State
`__flushw_user()` repeatedly performs `save` until `%otherwin` reaches zero, then restores back the same number of windows. `stack_trace_flush()` disables interrupts, walks restorable register windows by changing CWP, stores `%fp` and `%i7` to each window's stack slots, restores CWP and PSTATE, and returns. CPU ID helpers use `__GET_CPUID()`.

## Persistence and Dependencies
State changes are limited to transient register-window state, stack slots for frame pointer/return address, and interrupt-enable state during the flush. It depends on V9 window registers, stack bias, and CPU-ID macros.

## Integration Points, Risks, and Test Signals
Integration points include stack unwinding, debugging, SMP CPU identification, and any caller needing user windows materialized. Risks include interrupt-state restoration mistakes, bad stack slots if window layout changes, and CPU-ID macro mismatch for sun4v/sun4u. Test signals are reliable stack traces without full `flushw`, correct CPU IDs on SMP, and no register-window corruption during signal/debug tests.
