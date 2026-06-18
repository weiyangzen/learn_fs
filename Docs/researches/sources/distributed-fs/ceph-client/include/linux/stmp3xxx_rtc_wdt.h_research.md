<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmp3xxx_rtc_wdt.h -->
# sources/distributed-fs/ceph-client/include/linux/stmp3xxx_rtc_wdt.h

Purpose: Defines platform data for the STMP3xxx RTC watchdog integration.

Important APIs/types/functions: `struct stmp3xxx_wdt_pdata` with `wdt_set_timeout(struct device *dev, u32 timeout)`.

Control flow: Platform code supplies a timeout-setting callback that the watchdog/RTC driver can invoke with the target device and timeout value.

State and persistence behavior: No state in the header. Runtime state is the callback pointer and any platform-specific device registers it manipulates.

Dependencies: Uses `struct device` and `u32` via includer context.

Integration points: STMP3xxx RTC and watchdog drivers.

Risks: Callback lifetime and device pointer validity are critical. Timeout units must be consistently interpreted by provider and caller.

Test signals: Platform-data probe tests, watchdog timeout set tests, and null/missing callback handling in the consuming driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmp3xxx_rtc_wdt.h -->
