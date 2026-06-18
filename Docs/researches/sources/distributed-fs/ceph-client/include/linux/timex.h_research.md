<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timex.h -->
# sources/distributed-fs/ceph-client/include/linux/timex.h

## Purpose
declares NTP/adjtimex constants, frequency/phase scaling values, entropy cycle fallback hooks, and kernel adjtime/PPS entry points.

## Important APIs, Types, and Functions
The file is 165 lines and exports these visible symbol families: types/enums none; macros/constants `ADJ_ADJTIME`, `ADJ_OFFSET_SINGLESHOT`, `ADJ_OFFSET_READONLY`, `SHIFT_PLL`, `SHIFT_FLL`, `MAXTC`, `SHIFT_USEC`, `PPM_SCALE`, `PPM_SCALE_INV_SHIFT`, `PPM_SCALE_INV`, `MAXPHASE`, `MAXFREQ`, `MAXFREQ_SCALED`, `MINSEC`, and 6 more; function-like macros `random_get_entropy`, `shift_right`; inline helpers none; external prototypes `Copyright`, `do_adjtimex`, `do_clock_adjtime`, `hardpps`, `read_current_timer`.

## Control Flow
Clock adjustment syscalls call `do_adjtimex()` or `do_clock_adjtime()`, NTP code uses PLL/FLL constants and scaled PPM values to discipline the timekeeper, PPS code calls `hardpps()`, and architectures provide `get_cycles()` or the fallback entropy source.

## State and Persistence Behavior
The header stores no state, but constants govern NTP discipline state in timekeeping code and expose PIT tick rate defaults.

## Dependencies and Integration Points
It depends on UAPI timex, clock IDs, cycle counters, and architecture timer definitions; it integrates with NTP, PTP/PPS, random entropy sampling, and legacy PIT timing. Direct includes are `uapi/linux/timex.h`, `linux/compiler.h`, `linux/types.h`, `linux/param.h`, `asm/timex.h`.

## Risks and Edge Cases
Scaling constants and shift math are subtle. Overflow or sign errors in phase/frequency adjustment can destabilize system time. Entropy fallbacks must not promise more randomness than available.

## Test Signals
Run adjtimex/clock_adjtime selftests, NTP slew/step simulations, PPS tests, frequency boundary checks, and architecture builds with and without native cycle counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timex.h -->
