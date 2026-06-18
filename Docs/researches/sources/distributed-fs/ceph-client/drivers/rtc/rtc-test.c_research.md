# sources/distributed-fs/ceph-client/drivers/rtc/rtc-test.c

Purpose: software-only RTC test driver that creates three platform RTC devices for exercising RTC core behavior without hardware.

Important APIs/types/functions: `struct rtc_test_data` stores RTC, time offset, kernel timer alarm, and alarm enable flag. Time ops map RTC time to `ktime_get_real_seconds() + offset`; set-time updates offset. Alarm ops compute timer expiration from requested wall time minus offset, clamp jiffies expiration to `U32_MAX`, and use a `timer_list` callback to report `RTC_AF`. Device id 0 uses ops without read/set alarm; ids 1 and 2 include alarm ops and wakeup capability.

Control flow/state/persistence: module init registers the platform driver, allocates three platform devices, and adds them. Probe allocates private state, allocates RTC, selects ops based on id, initializes timer, and registers. Exit unregisters devices and driver. State is in RAM only and disappears on module unload.

Dependencies/integration: platform device/driver core, RTC core, kernel timers, jiffies, module init/exit.

Risks/test signals: alarm enable can add a timer even if no valid expiration has been programmed, and negative timeouts convert through unsigned arithmetic. This is a test fixture, so expected behavior should be documented in tests. Test three-device creation, no-alarm feature exposure on id 0, offset math, timer callback IRQ delivery, module unload cleanup, and alarm times in the past/far future.
