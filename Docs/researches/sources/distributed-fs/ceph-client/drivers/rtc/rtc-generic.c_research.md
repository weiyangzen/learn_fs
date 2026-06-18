# sources/distributed-fs/ceph-client/drivers/rtc/rtc-generic.c

Purpose: is a small platform wrapper that registers an RTC using `rtc_class_ops` supplied as platform data. It lets architecture or board code provide the actual RTC operations while reusing RTC class registration.

Important APIs/types/functions: `generic_rtc_probe()` obtains `const struct rtc_class_ops *ops` with `dev_get_platdata()`, registers a device named `rtc-generic` via `devm_rtc_device_register()`, and stores the returned RTC in platform driver data.

Control flow: `module_platform_driver_probe()` registers a probe-only platform driver named `rtc-generic`. Probe does no resource mapping and no validation beyond checking the returned RTC pointer.

State and persistence: this file owns no hardware or persistent state. All RTC state and behavior are delegated to platform-provided operations.

Dependencies and integration: depends on platform bus users passing a valid ops table, RTC core, and module alias `platform:rtc-generic`.

Risks and test signals: invalid or missing platform data would pass a NULL ops pointer into RTC registration depending on core validation. There is no OF/ACPI matching. Test platform-data registration, ops lifetime, read/set behavior provided by board code, and module unload/devres cleanup.
