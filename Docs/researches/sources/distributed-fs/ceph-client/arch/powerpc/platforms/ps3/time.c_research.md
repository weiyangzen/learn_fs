# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/time.c

Purpose: Provides PS3 timebase calibration, boot-time retrieval, and RTC platform-device registration.

Important APIs/types/functions: Implements `ps3_calibrate_decr()`, local `read_rtc()`, `ps3_get_boot_time()`, and device init `ps3_rtc_init()`.

Control flow: Decrementer calibration reads BE timebase frequency from the repository for BE index 0, stores it in `ppc_tb_freq`, and derives `ppc_proc_freq` as 40 times the timebase. Boot time reads LV1 RTC and adds PS3 OS-area RTC offset. Device init registers a simple `rtc-ps3` platform device only when PS3 LV1 firmware is present.

State and persistence: The file updates global PowerPC clock-frequency variables and relies on persistent OS-area RTC diff state. It holds no local mutable global state.

Dependencies and integration points: Depends on PS3 repository BE clock data, LV1 `lv1_get_rtc()`, PS3 OS-area helpers, PowerPC time setup, and the `rtc-ps3` driver.

Risks: Calibration and RTC reads use `BUG_ON()` on firmware errors, so bad repository/RTC data is fatal. The processor-frequency multiplier is PS3-specific. RTC platform-device creation has no resources and assumes the driver knows how to call platform helpers.

Test signals: Correct boot-time wall clock, stable decrementer/timer behavior, visible `rtc-ps3` platform device, RTC driver probe, and PS3 boot with repository BE clock data are useful.

Source read size: 59 lines, 1051 bytes.
