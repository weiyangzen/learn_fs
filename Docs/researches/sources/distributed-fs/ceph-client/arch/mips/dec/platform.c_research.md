# sources/distributed-fs/ceph-client/arch/mips/dec/platform.c

Purpose: registers DECstation RTC as a platform device.

Important APIs and data: `dec_rtc_resources` is filled at init with `RTC_PORT(0)` through `RTC_PORT(0) + dec_kn_slot_size - 1`; `dec_rtc_info` marks no periodic frequency support and 64-byte address space; `dec_add_devices()` registers `rtc_cmos`.

State and integration: depends on `dec_kn_slot_size` and `dec_rtc_base` established by PROM identification. Platform-device state persists in the driver core.

Risks and test signals: if PROM identification has not set slot size correctly, the RTC resource spans the wrong MMIO window. Verify `rtc_cmos` probe and persistent time reads on each supported DECstation family.
