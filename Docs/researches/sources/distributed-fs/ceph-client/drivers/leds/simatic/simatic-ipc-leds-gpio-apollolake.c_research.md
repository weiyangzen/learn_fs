<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c

Purpose: This module provides Apollo Lake GPIO lookup tables for SIMATIC IPC LED support and delegates the actual LED device creation to the shared GPIO core helper.

Important APIs and state: `simatic_ipc_led_gpio_table` maps six active-low GPIO lines on `apollolake-pinctrl.0` to the generic `leds-gpio` device indices. `simatic_ipc_led_gpio_table_extra` maps two additional GPIOs for `PM_BIOS_BOOT_N` and `PM_WDT_OUT`; its `dev_id` is filled by the core helper during probe. The platform driver hooks are `simatic_ipc_leds_gpio_apollolake_probe()` and `_remove()`.

Control flow: Probe calls `simatic_ipc_leds_gpio_probe(pdev, &table, &table_extra)`, which validates platform device mode, registers lookup tables, creates a `leds-gpio` platform device, and requests the extra lines as outputs. Remove delegates lookup-table cleanup and `leds-gpio` unregistration to the shared helper.

Dependencies and integration: The module depends on GPIO machine lookup tables, the Apollo Lake pinctrl provider, `leds-gpio`, and platform data from the SIMATIC IPC base driver. The soft dependency requests `simatic-ipc-leds-gpio-core` and `platform:apollolake-pinctrl` first.

Risks and test signals: Correct GPIO polarity and index ordering are the main behavioral risks. Test with an IPC127E-class platform that exposes the expected pinctrl label, confirm all six LED names toggle the intended front-panel LEDs, and verify remove unloads lookup tables before devices disappear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c -->
