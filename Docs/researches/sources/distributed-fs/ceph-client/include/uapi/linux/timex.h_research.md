# sources/distributed-fs/ceph-client/include/uapi/linux/timex.h

## Purpose
Defines NTP/adjtimex clock discipline UAPI for controlling and observing kernel time offset, frequency, error estimates, PLL/FLL/PPS status, TAI offset, and leap state.

## Important APIs, Types, and Constants
`NTP_API` is 4. Userspace `struct timex` is defined outside the kernel with old timeval fields. `struct __kernel_timex` is the time64/padded kernel ABI form with 64-bit fields and `__kernel_timex_timeval`. Mode constants include `ADJ_OFFSET`, `ADJ_FREQUENCY`, `ADJ_MAXERROR`, `ADJ_ESTERROR`, `ADJ_STATUS`, `ADJ_TIMECONST`, `ADJ_TAI`, `ADJ_SETOFFSET`, `ADJ_MICRO`, `ADJ_NANO`, `ADJ_TICK`, and legacy single-shot modes. Status constants include `STA_PLL`, PPS flags, leap flags, `STA_UNSYNC`, `STA_NANO`, read-only masks, and time states `TIME_OK`, `TIME_INS`, `TIME_DEL`, `TIME_OOP`, `TIME_WAIT`, and `TIME_ERROR`.

## Control Flow, State, and Persistence
Userspace calls `adjtimex`/`clock_adjtime` with mode bits. Kernel timekeeping updates or returns clock discipline state. Settings such as frequency and TAI offset persist in kernel until changed or rebooted.

## Dependencies and Integration Points
Depends on `<linux/time.h>`. Integrates with NTP/PTP daemons, PPS discipline, timekeeping core, and libc time APIs.

## Risks and Test Signals
Risks include old vs time64 struct confusion, privileged write controls, leap-second state handling, and read-only status bits. Test read-only queries, each writable mode with privilege checks, nanosecond/microsecond mode, TAI updates, PPS fields, and 32-bit Y2038-safe paths.
