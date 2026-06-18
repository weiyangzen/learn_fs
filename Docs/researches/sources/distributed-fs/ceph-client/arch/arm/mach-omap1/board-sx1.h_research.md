<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.h

Purpose: Siemens SX1 board header. It defines SOFIA companion-chip I2C address/register bits and declares board helper APIs shared with MMC and other board consumers.

Important APIs/types/functions: Declarations include `sx1_i2c_write_byte`, `sx1_i2c_read_byte`, light/power helpers, and `sx1_mmc_init`; macros define `SOFIA_*` registers and bit masks.

Control flow, state, and persistence: No state is stored in the header; SOFIA hardware registers are manipulated by the C files.

Dependencies and integration points: Declarations include `sx1_i2c_write_byte`, `sx1_i2c_read_byte`, light/power helpers, and `sx1_mmc_init`; macros define `SOFIA_*` registers and bit masks. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are ABI-like exported helper signatures and bit definitions drifting from hardware. Test compile users and SOFIA-controlled backlight/MMC/USB operations.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 45 lines, 1121 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.h -->
