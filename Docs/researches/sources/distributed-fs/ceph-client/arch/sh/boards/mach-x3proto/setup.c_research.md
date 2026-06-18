# sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/setup.c



Source read size: 270 lines, 5800 bytes.



Purpose: board file for the Renesas SH-X3 prototype board. It registers fixed platform devices for the heartbeat LED register, SMC91x Ethernet, R8A66597 USB host, M66592 USB peripheral, and GPIO-key baseboard buttons.

Important APIs/types/functions: `x3proto_devices_setup()`, `x3proto_init_irq()`, `x3proto_setup()`, the `mv_x3proto` machine vector, platform-device/resource tables, `smc91x_platdata`, `r8a66597_platdata`, `m66592_platdata`, and `gpio_keys_platform_data`.

Control flow: the machine vector setup registers SH-X3 SMP operations; the device initcall switches INTC pins to IRL mode, enables level mode in ICR0, initializes baseboard GPIOs, assigns dynamic GPIO numbers to the key table, maps ILSEL sources for LAN/USB interrupts, then calls `platform_add_devices()`.

State and persistence: device/resource tables are static kernel state; ILSEL allocations and GPIO base numbers become boot-time hardware routing state; no persistent storage is touched.

Dependencies and integration points: depends on X3Proto GPIO/ILSEL machine headers, SH interrupt pin setup, platform bus, SMC91x, Renesas USB host/peripheral drivers, gpio-keys, and SH-X3 SMP operations.

Risks and test signals: hard-coded physical addresses and ILSEL IDs must match the board wiring; interrupt polarity for USB host is low-triggered; button GPIO numbering depends on `x3proto_gpio_chip.base`. Test by booting the board, checking platform-device creation, LAN/USB interrupts, GPIO keys, heartbeat LED, and SMP bring-up.
