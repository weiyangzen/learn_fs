<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/delay.c

## Purpose
`delay.c` provides RISC-V busy-wait delay primitives backed by the cycle counter and calibrated loop constants.

## Important APIs, Types, And Functions
`__delay()` spins until a cycle delta elapses. `udelay()` converts microseconds to cycles, using a fast scaled `lpj_fine` path for small delays and `riscv_timebase` division for larger ones. `ndelay()` performs nanosecond conversion with a 64-bit scaled multiplier.

## Control Flow
`__delay()` snapshots `get_cycles()` and loops with `cpu_relax()`. `udelay()` chooses between fixed-point multiplication and direct timebase conversion based on `MAX_UDELAY_US`. `ndelay()` always uses the scaled nanosecond conversion.

## State And Persistence
The file reads `lpj_fine`, `riscv_timebase`, and the cycle counter. It stores no state.

## Dependencies And Integration Points
It integrates with kernel delay APIs and early/driver code that requires busy waits before scheduler timers are usable.

## Risks
Integer scaling constants assume `HZ <= 1000`. Very inaccurate timebase or cycle counter behavior affects all busy waits. Busy-wait delays burn CPU and must not be used for long sleeps.

## Test Signals
Boot timing sanity, driver delay-sensitive hardware tests, and build-time checks for HZ limits are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/delay.c -->
