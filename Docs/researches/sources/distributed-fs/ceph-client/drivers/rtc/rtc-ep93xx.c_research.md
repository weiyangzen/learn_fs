# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ep93xx.c

Purpose: supports the RTC block embedded in Cirrus Logic EP93xx processors. It exposes a seconds counter as the RTC and reports software compensation fields via procfs and sysfs.

Important APIs/types/functions: `struct ep93xx_rtc` stores the mapped MMIO base. `ep93xx_rtc_read_time()` reads `EP93XX_RTC_DATA`; `ep93xx_rtc_set_time()` writes seconds plus one to `EP93XX_RTC_LOAD`. `ep93xx_rtc_get_swcomp()` decodes preload/delete fields from `EP93XX_RTC_SWCOMP`. Sysfs attributes `comp_preload` and `comp_delete` expose compensation data.

Control flow: probe allocates state, maps the resource, allocates an RTC, attaches `ep93xx_rtc_ops`, sets `range_max = U32_MAX`, adds the sysfs group, and registers the device. There is no IRQ or alarm flow despite match/control registers existing in the hardware definition.

State and persistence: the hardware counter and compensation register are SoC state. Runtime state is just the MMIO base.

Dependencies and integration: integrates with platform/OF matching (`cirrus,ep9301-rtc`), MMIO, RTC core, procfs, and sysfs attribute groups.

Risks and test signals: `set_time()` writes `secs + 1`, so tests must verify this matches hardware load semantics and does not introduce off-by-one behavior. Alarm registers are unused. Test read/set round trips, compensation decoding, sysfs group registration failure, and U32 range boundary.
