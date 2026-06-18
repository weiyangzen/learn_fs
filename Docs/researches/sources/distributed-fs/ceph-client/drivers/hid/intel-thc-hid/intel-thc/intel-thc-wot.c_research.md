# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-wot.c

Purpose: optional Wake-on-Touch setup for Intel THC ACPI devices. It manually registers ACPI GPIO mappings, looks up a wake-capable GPIO interrupt, enables device wakeup, and installs a dedicated wake IRQ.

Important APIs: `thc_wot_config()` and `thc_wot_unconfig()` are exported in namespace `INTEL_THC`.

Control flow: config exits early for missing THC device or ACPI companion. It calls `acpi_dev_add_driver_gpios()`, retrieves `"wake-on-touch"` IRQ and wakeability, then calls `device_init_wakeup()` and `dev_pm_set_dedicated_wake_irq()`. Unconfig disables wakeup and clears/removes wake IRQ/GPIO mappings when they were established.

State and persistence: wake IRQ number and wakeable flag are stored in `thc_dev->wot`. PM wake state persists in the device core until unconfigured.

Dependencies and integration: depends on ACPI GPIO helpers and PM wakeirq support. Transport drivers provide the ACPI GPIO mapping and call this during probe/remove or PM setup.

Risks: failures are warnings, not probe blockers, so wake functionality can silently be absent while normal HID operation works. Mapping removal only happens when `gpio_irq > 0`.

Test signals: ACPI resource lookup logs, `/sys` wakeup state, suspend/resume wake tests using touch input, and remove/unbind cleanup.
