# sources/distributed-fs/ceph-client/include/linux/platform_data/bcm7038_wdt.h

Purpose: defines the platform-data hook for the Broadcom BCM7038 watchdog timer.

Important APIs and types: `struct bcm7038_wdt_platform_data` contains `const char *clk_name`, naming the clock used by the watchdog.

Control flow: platform setup passes the clock name to the watchdog driver; probe resolves the clock and uses its rate/control to program timeout behavior.

State and persistence: static clock binding data only. Runtime watchdog arming, timeout, and clock state live in the driver/hardware.

Dependencies and integration points: integrates Broadcom platform devices, common clock framework lookup by name, and watchdog subsystem registration.

Risks and test signals: risks include wrong or missing clock names leading to timeout miscalculation or probe failure. Test probe with valid/invalid clock names, watchdog start/stop/ping, timeout programming, and suspend/resume clock behavior.
