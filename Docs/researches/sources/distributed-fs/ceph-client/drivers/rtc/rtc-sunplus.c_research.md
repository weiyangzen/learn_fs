# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sunplus.c

Purpose: RTC driver for Sunplus SP7021. It exposes a 32-bit seconds counter, absolute alarm register, alarm IRQ, reset/clock management, wakeup, and optional trickle charger configuration from DT.

Important APIs/types/functions: `struct sunplus_rtc` stores RTC, resource pointer, clock, reset, MMIO, and IRQ. `sp_get_seconds()`/`sp_set_seconds()` access timer registers. RTC ops convert seconds to/from `rtc_time`, read/write alarm seconds, and control alarm bits in `RTC_CTRL`. `sp_rtc_set_trickle_charger()` parses `trickle-resistor-ohms` and `aux-voltage-chargeable` to program battery charger resistance/diode/enable bits.

Control flow/state/persistence: probe maps named `rtc` resource, requests rising-edge IRQ, enables clock, deasserts reset, marks wakeup, allocates/registers RTC with U32 range, configures trickle charger if DT properties exist, and sets `DIS_SYS_RST_RTC` to preserve RTC through system reset. Remove disables wakeup, asserts reset, and disables clock.

Dependencies/integration: compatible `sunplus,sp7021-rtc`, platform named resource, clock/reset frameworks, DT properties for charger, RTC core, IRQ wake PM.

Risks/test signals: `struct resource *res` is logged but never assigned. Alarm read treats `RTC_ALARM_SET == 0` as disabled, so a legitimate epoch alarm cannot be represented. Test clock/reset error unwinds, trickle charger valid/invalid values, alarm enable bitmask writes, wake IRQ suspend/resume, and U32 rollover.
