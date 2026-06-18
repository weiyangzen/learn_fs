<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-f7188x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-f7188x.c

Purpose: This board wrapper handles SIMATIC GPIO LEDs wired through Nuvoton F7188x GPIO controllers, with different lookup tables for IPC227G and BX-59A device modes.

Important APIs and state: `struct simatic_ipc_led_tables` stores selected primary and extra lookup tables in platform driver data. IPC227G uses six active-low LED lines from `gpio-f7188x-2` and two active-high extra outputs from `gpio-f7188x-3`. BX-59A uses a six-line active-low table spread across `gpio-f7188x-2`, `gpio-f7188x-5`, and `gpio-f7188x-7`.

Control flow: Probe allocates table-selection state, switches on `plat->devmode`, stores the selected tables with `platform_set_drvdata()`, then calls the common GPIO probe. Remove retrieves the table pointers and calls common cleanup.

Dependencies and integration: The module relies on `GPIO_F7188X`, the shared SIMATIC GPIO helper, the SIMATIC platform base driver, and generic `leds-gpio`. The soft dependency names `gpio_f7188x` and the core helper.

Risks and test signals: Device-mode selection is the main source of correctness. Missing extra table handling must be valid for BX-59A. Test both device modes, confirm table index ordering and polarity, and verify that a default/unknown `devmode` returns `-ENODEV` without registering lookup tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-f7188x.c -->
