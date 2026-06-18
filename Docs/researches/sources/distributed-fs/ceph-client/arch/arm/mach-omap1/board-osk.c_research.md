<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-osk.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-osk.c

Purpose: Board support for TI OMAP5912 OSK. It configures NOR flash, SMC91x Ethernet, CompactFlash, TPS65010 PMIC GPIOs/LEDs/regulators, USB host/device mode, I2C devices, serial, and board EMIFS timing workarounds.

Important APIs/types/functions: Key routines are `osk_tps_setup`, `osk_tps_teardown`, `osk_init_smc91x`, `osk_init_cf`, and `osk_init`; the machine descriptor is `OMAP_OSK`.

Control flow, state, and persistence: State includes platform devices/resources, flash partitions, TPS GPIO descriptors held for board lifetime, LED lookup tables, USB/IRQ GPIO tables, and I2C board info. Init patches IRQ resources from GPIO descriptors before platform registration.

Dependencies and integration points: Key routines are `osk_tps_setup`, `osk_tps_teardown`, `osk_init_smc91x`, `osk_init_cf`, and `osk_init`; the machine descriptor is `OMAP_OSK`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include TPS65010, SMC91x, physmap flash, omap_cf, OHCI/UDC selection, OMAP GPIO, I2C, and EMIFS registers. Risks are unchecked GPIO request failures in PMIC setup, hard-coded CS timings, and config-dependent USB mode. Test Ethernet RX/TX, CF IRQ, flash partitions/VPP, PMIC LEDs, USB power/overcurrent, and I2C IRQ.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 454 lines, 12694 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-osk.c -->
