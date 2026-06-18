<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1-mmc.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1-mmc.c

Purpose: Siemens SX1 MMC glue. It powers the MMC slot through the SOFIA I2C companion chip and registers OMAP MMC controller data when MMC support is enabled.

Important APIs/types/functions: Important functions are `mmc_set_power` and `sx1_mmc_init`. The power callback uses `sx1_i2c_read_byte`/`sx1_i2c_write_byte` on `SOFIA_POWER1_REG` and toggles `SOFIA_MMC_POWER`.

Control flow, state, and persistence: State is static MMC platform data and the SOFIA power register bit. No kernel-side persistent object is stored beyond registration.

Dependencies and integration points: Important functions are `mmc_set_power` and `sx1_mmc_init`. The power callback uses `sx1_i2c_read_byte`/`sx1_i2c_write_byte` on `SOFIA_POWER1_REG` and toggles `SOFIA_MMC_POWER`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include SX1 board I2C helpers, SOFIA register constants, and OMAP MMC support. Risks are I2C adapter 0 availability during power callbacks and lack of cover-switch handling. Test MMC insertion/removal, power cycling, and builds with `CONFIG_MMC_OMAP` disabled.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 62 lines, 1356 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1-mmc.c -->
