<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-core.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-core.c

Purpose: This shared module implements the common probe/remove path for SIMATIC IPC GPIO-based LEDs. Board-specific wrappers provide GPIO lookup tables; this file registers a generic `leds-gpio` platform device with six named status LEDs.

Important APIs and state: `simatic_ipc_gpio_leds[]` defines red/green status LED names for status groups 1 through 3. `simatic_ipc_gpio_leds_pdata` is passed to `platform_device_register_resndata()`. `simatic_leds_pdev` stores the singleton `leds-gpio` device. Exported symbols `simatic_ipc_leds_gpio_probe()` and `simatic_ipc_leds_gpio_remove()` are used by the Apollo Lake, Elkhart Lake, and F7188x modules.

Control flow: Probe checks `plat->devmode` and accepts 127E, 227G, BX-21A, and BX-59A. It adds the primary lookup table, registers `leds-gpio`, then optionally adds an extra lookup table scoped to the SIMATIC platform device and requests indices 6 and 7 as low outputs for BIOS boot and watchdog output control. Any failure calls the remove helper to unwind lookup tables and the child platform device. Remove removes both lookup tables and unregisters the singleton child platform device.

State and persistence: State is limited to the global child platform-device pointer and kernel GPIO lookup-table registration. LED state is managed by the generic `leds-gpio` driver after registration.

Risks and test signals: The helper assumes a single active GPIO LED device; concurrent multiple SIMATIC platform devices would collide through `simatic_leds_pdev`. `gpiod_remove_lookup_table(NULL)` must remain tolerated for wrappers that pass no extra table. Test accepted and rejected `devmode` values, error unwind after `leds-gpio` registration, and extra GPIO request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-core.c -->
