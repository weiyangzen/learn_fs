<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Makefile

Purpose: OMAP1 object list. It links common SoC support, clocks, timers, reset, PM, optional I2C/USB/MCBSP support, board files, FIQ code, and SoC-specific GPIO implementations.

Important APIs/types/functions: The main integration is Kbuild object selection through `obj-y`, `obj-$(CONFIG_...)`, and conditional composite variables.

Control flow, state, and persistence: No runtime state exists; build inclusion determines which initcalls and machine descriptors are present.

Dependencies and integration points: The main integration is Kbuild object selection through `obj-y`, `obj-$(CONFIG_...)`, and conditional composite variables. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are accidental inclusion of board glue in multi-board kernels or missing companion assembly for AMS Delta FIQ. Test builds for each board and with optional USB/I2C/MMC/PM toggles.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 41 lines, 1110 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Makefile -->
