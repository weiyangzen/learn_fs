<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/timex.h

## Purpose
Provides OpenRISC cycle-counter access for generic timekeeping and delay loops.

## Important APIs, Types, And Functions
Defines `get_cycles()` to read `SPR_TTCR` through `mfspr()`. Sets `CLOCK_TICK_RATE` to `1000` as a legacy value and declares `ARCH_HAS_READ_CURRENT_TIMER`.

## Control Flow
Delay and clocksource code call `get_cycles()` repeatedly. No control flow is implemented here beyond the inline SPR read.

## State And Persistence
Reads the hardware tick timer counter; it does not mutate state.

## Dependencies And Integration Points
Depends on `asm-generic/timex.h`, `spr.h`, and `spr_defs.h`. Used by `lib/delay.c` and `kernel/time.c`.

## Risks
If TTCR is stopped or absent, delays and clocksource reads are invalid. Wraparound is 32-bit and callers must use delta arithmetic.

## Test Signals
Delay calibration, monotonic clocksource reads across wraps, and `read_current_timer()` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/timex.h -->
