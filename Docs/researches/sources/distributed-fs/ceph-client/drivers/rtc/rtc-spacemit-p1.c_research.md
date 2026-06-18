# sources/distributed-fs/ceph-client/drivers/rtc/rtc-spacemit-p1.c

Purpose: RTC driver for the SpacemiT P1 PMIC. It exposes time read/write only over the parent PMIC regmap and explicitly disables alarm/update interrupt RTC features.

Important APIs/types/functions: `struct p1_rtc` stores regmap and RTC device. `p1_rtc_read_time()` checks `RTC_EN`, then reads the six-byte time block until two successive second values match, working around unstable hardware latching. `p1_rtc_set_time()` disables the RTC, writes six raw fields, and re-enables it. Probe gets the parent regmap, allocates/registers RTC, sets range 2000..2063, and clears alarm/update features.

Control flow/state/persistence: time registers store seconds, minutes, hours, zero-based day-of-month, zero-based month, and year since 2000. Set-time leaves RTC disabled if the bulk write fails, matching the comment that partially updated time should not run.

Dependencies/integration: platform MFD child named `spacemit-p1-rtc`, parent regmap, RTC core, module alias `platform:spacemit-p1-rtc`.

Risks/test signals: comments say hours are documented as 0-59 but the driver masks them with 5 bits, so hardware documentation and runtime validation should be checked. Read stability relies only on identical seconds, not whole-buffer equality. Test disabled RTC reads, unstable second rollover loops, day/month conversions, 2063 boundary, failed writes leaving RTC disabled, and feature bits exposed to userspace.
