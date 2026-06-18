<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/lib/delay.c

## Purpose
Implements precise OpenRISC busy-wait delay loops using the tick timer counter.

## Important APIs, Types, And Functions
`read_current_timer()` returns `get_cycles()`. `__delay()` spins until a cycle delta elapses. `__const_udelay()`, `__udelay()`, and `__ndelay()` scale micro/nanosecond inputs through `loops_per_jiffy` and `HZ`.

## Control Flow
Delay calls sample `get_cycles()` and loop with `cpu_relax()` until unsigned delta reaches the requested count.

## State And Persistence
Reads TTCR and `loops_per_jiffy`; no persistent state.

## Dependencies And Integration Points
Depends on `timex.h`, delay API, calibrated loops from `setup.c`, and exported symbols for modules.

## Risks
Accuracy depends on CPU clock frequency and running tick timer. Large delays rely on wrap-safe arithmetic but still busy-wait.

## Test Signals
Delay calibration output, timer-based delay tests, driver polling delays, and module references to exported delay helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/delay.c -->
