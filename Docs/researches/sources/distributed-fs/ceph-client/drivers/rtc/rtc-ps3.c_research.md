# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ps3.c

Purpose: provides a minimal PlayStation 3 platform RTC backed by the hypervisor RTC value plus an OS-area offset.

Important APIs/types/functions: `read_rtc()` calls `lv1_get_rtc()` and returns the hypervisor RTC value. `ps3_get_time()` reports `read_rtc() + ps3_os_area_get_rtc_diff()`. `ps3_set_time()` stores the requested wall-clock delta through `ps3_os_area_set_rtc_diff()`. `ps3_rtc_probe()` allocates and registers the RTC device.

Control flow: platform probe allocates an RTC, installs read/set ops, sets the maximum range to `U64_MAX`, stores the RTC as platform data, and registers it. There is no interrupt, alarm, suspend/resume, or cleanup-specific logic beyond devm.

State and persistence: the raw RTC is owned by PS3 firmware/hypervisor. Linux persists wall-clock changes as an OS-area difference rather than writing the hypervisor clock itself.

Dependencies and integration: depends on PS3 architecture headers, LV1 hypervisor calls, PS3 OS area helpers, platform device binding, and RTC core.

Risks: `read_rtc()` uses `BUG_ON(result)`, so an unexpected hypervisor failure panics the kernel. No alarm or validity reporting is present. Test signals include successful platform probe, read/set offset round trip, OS-area persistence across reboot, and behavior under hypervisor call failure in architecture-specific tests.
