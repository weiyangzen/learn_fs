# sources/distributed-fs/ceph-client/arch/mips/cobalt/rtc.c

Purpose: registers the Cobalt MC146818-compatible RTC.

Important APIs: `cobalt_rtc_add()` allocates `"rtc_cmos"`, adds I/O resource `0x70..0x77` and IRQ `RTC_IRQ`, then registers it at `device_initcall`.

State and integration: no mutable local state; RTC resources are owned by the platform device and consumed by the CMOS RTC driver.

Risks and test signals: IRQ/resource mismatch breaks clock reads or alarms. Verify `rtc_cmos` probe, `/dev/rtc*`, and persistent-clock reads.
