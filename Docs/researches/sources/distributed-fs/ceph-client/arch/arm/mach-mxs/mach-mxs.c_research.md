<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/mach-mxs.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mxs/mach-mxs.c

Purpose: Device-tree machine support for Freescale MXS. It reads OCOTP fuses, patches Ethernet MAC addresses, registers SoC metadata, runs board-specific fixups, populates DT devices, and installs a restart handler.

Important APIs/types/functions: Important functions include `mxs_get_ocotp`, `update_fec_mac_prop`, board init helpers, `mxs_get_soc_id`, `mxs_get_cpu_rev`, `mxs_restart_init`, `mxs_machine_init`, and `mxs_restart`.

Control flow, state, and persistence: The control path caches OCOTP words under a mutex, maps DIGCTL to derive chip/revision, registers a `soc_device`, applies compatible-string fixups for EVK/APF28/APX4/Crystalfontz/Duckbill/M28CU3, then maps CLKCTRL reset registers.

Dependencies and integration points: Important functions include `mxs_get_ocotp`, `update_fec_mac_prop`, board init helpers, `mxs_get_soc_id`, `mxs_get_cpu_rev`, `mxs_restart_init`, `mxs_machine_init`, and `mxs_restart`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: State includes cached OCOTP words, `chipid`, `socid`, system serial fields, and `reset_addr`. Dependencies include DT, OCOTP/DIGCTL/CLKCTRL registers, clk helpers, PHY fixups, SoC bus, and platform population. Risks include unchecked OCOTP map failures, board OUI hard-coding, and reset fallback through address zero. Test MAC fixups, SoC sysfs, board quirks, reboot, and OCOTP timeout handling.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 480 lines, 10610 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/mach-mxs.c -->
