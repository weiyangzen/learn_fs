<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/delay.h

## Purpose
Provides busy-wait delay primitives for Xtensa using simple instruction loops and the cycle counter.

## Important APIs, Types, And Functions
Defines `__delay`, `__udelay`, `udelay`, `__ndelay`, `ndelay`, `__bad_udelay`, `__bad_ndelay`, and uses `loops_per_jiffy`, `get_ccount`, and `ccount_freq`.

## Control Flow
`__delay` emits a nop for tiny constant delays or decrements by two cycles per loop. `__udelay` computes cycle count from microseconds and spins on `ccount` with wraparound-safe subtraction. `__ndelay` scales nanoseconds to cycles and delegates to `__delay`. Compile-time too-large constants call undefined symbols to trigger build errors.

## State And Persistence
No persistent state; reads the cycle counter and clock frequency.

## Dependencies And Integration Points
Depends on Xtensa timer/cycle-counter setup and generic delay API users.

## Risks And Edge Cases
Correctness depends on calibrated `ccount_freq`, wraparound arithmetic, and interrupt/preemption effects. Large delay constants intentionally fail at link time.

## Test Signals
Timer calibration tests, driver delay smoke tests, and measurements of udelay/ndelay accuracy across CPU frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/delay.h -->
