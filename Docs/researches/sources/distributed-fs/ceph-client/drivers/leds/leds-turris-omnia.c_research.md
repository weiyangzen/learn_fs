# sources/distributed-fs/ceph-client/drivers/leds/leds-turris-omnia.c

Purpose: I2C LED driver for the CZ.NIC Turris Omnia MCU LED controller. It exposes up to twelve RGB multicolor LEDs, a private hardware trigger for MCU control, and controller-wide brightness/gamma sysfs attributes.

Important APIs, types, and functions: `struct omnia_led` stores multicolor LED state, cached RGB channels, on/off state, hardware-trigger state, and MCU LED number. `struct omnia_leds` stores client, mutex, feature flags, brightness sysfs knode, and LED array. `omnia_led_brightness_set_blocking()` sends color and state commands. `omnia_hwtrig_activate()`/`_deactivate()` switch MCU/software mode. `omnia_led_register()` validates DT and registers each multicolor LED. Controller attributes use `OMNIA_CMD_GET/SET_BRIGHTNESS` and gamma commands.

Control flow: probe counts child LEDs, queries the sibling MCU at address 0x2a for supported features, optionally requests a brightness-change IRQ, registers the private trigger, and registers each valid child LED. Brightness changes recalculate RGB with `led_mc_calc_color_components()`, avoid redundant color commands through cached channels, and then send state changes when needed.

State and persistence: cached per-channel values and `on/hwtrig` booleans prevent redundant MCU commands and preserve mode decisions. Remove restores all LEDs to default hardware-triggered white mode. Brightness sysfs notification caches a kernfs node after the first IRQ.

Dependencies and integration points: Turris Omnia MCU command interface, I2C, LED multicolor and trigger APIs, OF child nodes, sysfs attributes, threaded IRQ, and MCU feature discovery.

Risks and test signals: test feature detection fallback, missing IRQ with brightness interrupt support, gamma unsupported writes, hardware-trigger transitions while off, cached color consistency, invalid child nodes being skipped, and remove-time global restore. Commands share MCU state with other Omnia functions, so cross-driver integration matters.
