<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/common.h

Purpose: Shared OMAP1 internal declaration header. It ties board files and common machine code to timer, IRQ, IO, serial, USB, reset, clock, mux, and late-init routines.

Important APIs/types/functions: It declares routines such as `omap1_map_io`, `omap1_init_early`, `omap1_init_irq`, `omap1_timer_init`, `omap1_init_late`, `omap1_restart`, `omap_serial_init`, and optional device helpers.

Control flow, state, and persistence: No state is stored here, but the header defines cross-file integration contracts for machine descriptors.

Dependencies and integration points: It declares routines such as `omap1_map_io`, `omap1_init_early`, `omap1_init_irq`, `omap1_timer_init`, `omap1_init_late`, `omap1_restart`, `omap_serial_init`, and optional device helpers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are declaration drift and board files depending on legacy global init order. Test all OMAP1 board builds and link-time coverage.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 78 lines, 2395 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/common.h -->
