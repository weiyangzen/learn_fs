<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-nokia770.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-nokia770.c

Purpose: Board support for the Nokia 770 Internet Tablet. It registers keypad, LCD MIPID, ADS7846 touchscreen, USB, MMC, CBUS/I2C Retu/Tahvo devices, GPIO software nodes, IRQ lookup tables, and OMAP serial/display setup.

Important APIs/types/functions: Important functions are `mipid_dev_init`, `hwa742_dev_init`, `nokia770_mmc_init`, `nokia770_cbus_init`, and `omap_nokia770_init`; the machine descriptor is `NOKIA770`.

Control flow, state, and persistence: State consists of static platform data, SPI board info, software nodes, GPIO lookup tables, and optional MMC/I2C data. Init unblocks SleepX, registers GPIO chip nodes, patches IRQ numbers from descriptors, then registers SPI/I2C/USB/MMC.

Dependencies and integration points: Important functions are `mipid_dev_init`, `hwa742_dev_init`, `nokia770_mmc_init`, `nokia770_cbus_init`, and `omap_nokia770_init`; the machine descriptor is `NOKIA770`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include gpio descriptors, SPI, omapfb, CBUS GPIO I2C, Retu/Tahvo, MMC OMAP, and USB extcon name `tahvo-usb`. Risks are optional-config stubs, GPIO descriptor lifetime leaks, and hard-coded board IRQ mappings. Test touchscreen IRQ, LCD reset, MMC cover/power, Retu/Tahvo interrupts, USB extcon, and serial wake.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 351 lines, 9174 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-nokia770.c -->
