# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas-rtc.c

## Purpose
`rtas-rtc.c` implements RTAS-backed real-time clock operations for boot time, read time, and set time.

## Important APIs, Types, And Functions
It provides `rtas_get_boot_time()`, `rtas_get_rtc_time()`, and `rtas_set_rtc_time()`. It uses RTAS tokens `RTAS_FN_GET_TIME_OF_DAY` and `RTAS_FN_SET_TIME_OF_DAY`, `rtas_busy_delay_time()`, timebase helpers, `mktime64()`, `rtc_time`, `msleep()`, and `udelay()`.

## Control Flow
Each function calls the relevant RTAS method in a loop while RTAS reports busy delay and a five-second `MAX_RTC_WAIT` timebase budget has not expired. Boot-time read spins with `udelay()` because scheduling is not available. Normal read/set uses `msleep()` but refuses to delay in interrupt context; read clears the output time on would-delay interrupt context, while set returns `1`. Successful reads translate RTAS year/month/day/hour/min/sec fields into `time64_t` or `struct rtc_time`; set passes converted fields to RTAS.

## State And Persistence
There is no local persistent state. `rtas_set_rtc_time()` changes firmware/hardware RTC state.

## Dependencies And Integration Points
The file plugs into PowerPC time/RTC machine operations and depends on RTAS core token lookup, busy-delay interpretation, and timebase frequency.

## Risks
Interrupt-context behavior is intentionally limited; callers may receive unchanged/zeroed time instead of sleeping. Busy loops stop after five seconds but still return or log based on the final RTAS error. The functions trust RTAS return field ordering.

## Test Signals
Exercise successful get/set, RTAS busy retry, timeout behavior, interrupt-context read and set paths, error logging, month/year conversion boundaries, and boot-time read before scheduler availability.
