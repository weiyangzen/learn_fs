# sources/distributed-fs/ceph-client/drivers/platform/x86/pcengines-apuv2.c

Purpose: This module creates board-specific GPIO, LED, and polled-key platform devices for PC Engines APU2/APU3/APU4 boards using the AMD FCH GPIO controller. It turns DMI-detected board wiring into standard `gpio-amd-fch`, `leds-gpio`, and `gpio-keys-polled` devices.

Important APIs, types, and functions: `board_apu2` is `amd_fch_gpio_pdata` describing FCH GPIO registers and names. Software nodes (`apu2_gpiochip_node`, LED child nodes, key node) describe firmware-like properties for GPIO consumers. `apu_create_pdev()` wraps `platform_device_register_full()`. `apu_board_init()` gates on `apu_gpio_dmi_table`, registers software nodes, then creates GPIO, LED, and key devices.

Control flow: Module init DMI-matches several legacy/mainline BIOS naming variants, registers a software-node hierarchy, registers the AMD FCH GPIO platform device with board pdata, then registers the `leds-gpio` and `gpio-keys-polled` consumers. Failure unwinds in reverse order. Module exit unregisters keys, LEDs, GPIO, and software nodes.

State and persistence: State is static platform-device pointers and software-node data. Hardware state belongs to GPIO/LED child drivers after instantiation. There is no persistent configuration or runtime mutation inside this file.

Dependencies and integration points: The module depends on DMI, `gpio-amd-fch` platform data, generic software-node property handling, LED GPIO binding semantics, GPIO keys polled binding semantics, and `MODULE_SOFTDEP` to load required platform drivers first.

Risks and edge cases: DMI matching uses string-prefix-like board-name variants, and the comment warns APU1 is incompatible. GPIO register order must match the line indexes referenced by software-node GPIO properties. Because it creates global platform devices, partial registration failure must unwind exactly or stale software nodes/GPIO consumers may remain.

Test signals: Test on APU2, APU3, and APU4 DMI variants; verify named GPIO lines, active-low front LEDs, and front-button `KEY_RESTART` events. Failure-injection should confirm each unwind label unregisters previously created devices.
