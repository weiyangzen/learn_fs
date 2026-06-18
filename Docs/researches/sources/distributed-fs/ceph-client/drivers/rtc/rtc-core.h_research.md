# sources/distributed-fs/ceph-client/drivers/rtc/rtc-core.h

## Purpose
Internal RTC core header that declares or stubs optional RTC character-device, procfs, and sysfs integration hooks based on kernel configuration.

## Important APIs, types, and functions
- Under `CONFIG_RTC_INTF_DEV`, declares `rtc_dev_init()` and `rtc_dev_prepare(struct rtc_device *rtc)`; otherwise provides empty inline stubs.
- Under `CONFIG_RTC_INTF_PROC`, declares `rtc_proc_add_device()` and `rtc_proc_del_device()`; otherwise provides empty inline stubs.
- Under `CONFIG_RTC_INTF_SYSFS`, declares `rtc_get_dev_attribute_groups()` returning attribute group arrays; otherwise returns `NULL`.

## Control flow
There is no runtime logic beyond compile-time selection. RTC core users can call these helpers unconditionally and rely on no-op stubs when optional interfaces are disabled.

## State and persistence behavior
No state is stored here. It only controls symbol visibility and optional subsystem integration at compile time.

## Dependencies and integration points
Depends on `struct rtc_device` being visible to includers. Integrates RTC core internals with dev node setup, proc registration, and sysfs attribute grouping.

## Risks
The main risk is configuration skew: code that assumes dev/proc/sysfs side effects must tolerate no-op stubs when options are disabled.

## Test signals
Build coverage for `CONFIG_RTC_INTF_DEV`, `CONFIG_RTC_INTF_PROC`, and `CONFIG_RTC_INTF_SYSFS` enabled and disabled; runtime checks that optional interfaces appear only when configured.
