# sources/distributed-fs/ceph-client/drivers/rtc/rtc-au1xxx.c

## Purpose

`rtc-au1xxx.c` exposes the Au1xxx Time-Of-Year counter as an RTC. Counter 0 counts seconds from the Unix epoch using an external 32.768 kHz crystal and continues during sleep or powerdown when configured by firmware or board code.

## Important APIs, types, and functions

RTC callbacks are `au1xtoy_rtc_read_time()` and `au1xtoy_rtc_set_time()`. Probe checks counter control bits `SYS_CNTRL_E0` and `SYS_CNTRL_32S`, sets the TOY trim register to 32767 for a 1 Hz tick if needed, waits for hardware write access, allocates/registers the RTC, and sets `range_max = U32_MAX`.

## Control flow

Read time reads `AU1000_SYS_TOYREAD` through `alchemy_rdsys()` and converts seconds to `rtc_time`. Set time writes seconds to `AU1000_SYS_TOYWRITE`, then waits while `SYS_CNTRL_C0S` indicates a pending counter write. Probe waits for trim access through `SYS_CNTRL_T0S` with a large timeout and fails if access never becomes available.

## State and persistence behavior

Hardware persists the TOY counter and trim configuration in Au1xxx system registers. The driver has no private state beyond the registered RTC device. It assumes bootloader or board code has enabled and clocked the counters.

## Dependencies and integration points

It depends on Alchemy/Au1xxx architecture system register helpers from `<asm/mach-au1x00/au1000.h>`, platform devices, and RTC class APIs. It is registered with platform name `"rtc-au1xxx"`.

## Risks and edge cases

Set-time waits for up to about six seconds without a timeout in the final counter-write wait. Probe explicitly does not verify the actual 32 kHz clock quality because that would be too slow. There is no alarm or wake support. The range is limited to 32-bit seconds.

## Test signals

Test probe failure when counter status bits are absent, trim programming and timeout path, set/read round trips, behavior while counter write pending, persistence through sleep/powerdown, and absence of alarm ioctls.
