<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.c

Purpose: Board support for the Amstrad E3/Delta videophone. It maps board latches/modem space, configures keypad, NAND, LCD, LEDs, audio, codec, modem UART, fixed regulators, GPIO lookup tables, FIQ keyboard support, USB, I2C, serial, and OMAP muxing.

Important APIs/types/functions: Key routines are `omap_gpio_deps_init`, `ams_delta_latch2_init`, `ams_delta_init`, `modem_pm`, `ams_delta_modem_pm_activate`, `ams_delta_modem_init`, and `ams_delta_map_io`; the machine descriptor is `AMS_DELTA`.

Control flow, state, and persistence: State includes latch initial values, GPIO lookup tables, software nodes, modem regulator private data, platform devices, flash partitions, and FIQ-updated serio resources. Init ordering is critical: OMAP GPIO deps, latch safety, devices, latch GPIO providers, regulator names, lookup tables, then LEDs.

Dependencies and integration points: Key routines are `omap_gpio_deps_init`, `ams_delta_latch2_init`, `ams_delta_init`, `modem_pm`, `ams_delta_modem_pm_activate`, `ams_delta_modem_init`, and `ams_delta_map_io`; the machine descriptor is `AMS_DELTA`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP GPIO postcore init, FIQ code, basic-mmio-gpio, regulator/fixed-voltage, serial8250, gpio-nand, omapfb, USB, and legacy ATAGS. Risks are fragile dev_name patching, deliberate GPIO descriptor leaks, unsafe latch defaults, and modem probe ordering. Test boot, NAND access, LCD, LEDs, keyboard FIQ/serio, modem UART PM, and regulator probe deferral.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 873 lines, 24023 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.c -->
