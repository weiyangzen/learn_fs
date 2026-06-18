# sources/distributed-fs/ceph-client/arch/m68k/bvme6000/rtc.c

Purpose: misc-device `/dev/rtc` interface for the BVME6000 DP8570A real-time clock.

Important functions are `rtc_ioctl()`, `rtc_open()`, `rtc_release()`, and `rtc_DP8570A_init()`. Supported ioctls are `RTC_RD_TIME` and `RTC_SET_TIME`. Reads snapshot BCD RTC fields while ensuring seconds are stable across the read. Writes require `CAP_SYS_ADMIN`, validate month/day/leap-year/hour/min/sec/year bounds, and program BCD fields plus leap-year state.

State is hardware RTC registers and `rtc_status`, an atomic single-open guard initialized to one. `rtc_open()` decrements and tests atomically, returning `-EBUSY` if already open; release increments it.

Dependencies include BVME hardware register definitions, miscdevice APIs, uaccess, BCD conversion, capability checks, and `MACH_IS_BVME6000`. Integration is separate from `mach_hwclk` in `config.c` but accesses the same hardware.

Risks and test signals: concurrent hardware clock and misc RTC access are only locally IRQ-protected, not globally locked with `mach_hwclk`; date validation rejects years >= 2070. Test open exclusivity, read stability, permission failure for unprivileged set, leap-day validation, and matching values between `/dev/rtc` and kernel hwclk.
