<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.c

Purpose: implements the Samsung S3C6410/Exynos3250 internal MMIO RTC with time, alarm, wakeup, SoC-specific enable/disable hooks, and clock-gated register access.

Important APIs/types/functions: `struct s3c_rtc` stores device/RTC pointers, MMIO base, RTC and source clocks, alarm state, SoC data, alarm IRQ, spinlock, and wake flag. `struct s3c_rtc_data` supplies per-compatible clock needs and callbacks. Core functions include `s3c_rtc_enable_clk()`, `s3c_rtc_disable_clk()`, `s3c_rtc_setaie()`, `s3c_rtc_read_time()`, `s3c_rtc_write_time()`, `s3c_rtc_getalarm()`, `s3c_rtc_setalarm()`, `s3c6410_rtc_enable()`, `s3c6410_rtc_disable()`, and PM callbacks.

Control flow: probe reads match data, gets alarm IRQ and MMIO resource, prepares/enables required clocks, disables bootloader RTC bits, re-enables/normalizes RTCCON, initializes wakeup, allocates/registers RTC, requests alarm IRQ, then gates clocks off. Time reads enable clocks, read BCD fields, retry once if seconds are zero to avoid mid-update reads, convert to 2000-2099, and disable clocks. Alarm set writes only valid fields, builds enable bits, and calls `s3c_rtc_setaie()`. Suspend disables RTC hardware and optionally enables IRQ wake; resume re-enables hardware and disables wake.

State and persistence: hardware persists BCD time, alarm registers, RTCCON, RTCALM, and interrupt-pending bits. Driver state tracks whether alarm IRQ enable is holding an extra clock reference so alarms can fire while normal access is gated.

Dependencies and integration points: depends on platform MMIO, Samsung register definitions from `rtc-s3c.h`, clocks `rtc` and `rtc_src`, RTC core, IRQ wake support, OF compatibles `samsung,s3c6410-rtc` and `samsung,exynos3250-rtc`.

Risks and test signals: `s3c_rtc_setaie()` manipulates clock references in nested ways and must balance normal access with alarm-held clocks. The driver explicitly does not support pre-2000 dates. Alarm year is read but never set in `s3c_rtc_setalarm()`. Test clock prepare/enable unwind, alarm enable/disable clock balance, seconds-zero retry, partial alarm masks, suspend/resume wake, RTCCON cleanup, IRQ pending clear, and invalid date range behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.c -->
