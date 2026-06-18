<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.c

Purpose: MVEBU SoC identification support. It discovers Armada SoC device/revision IDs either through system-controller helpers or, for Armada 370/XP, through PCI vendor/device/class configuration space, then registers a Linux `soc_device`.

Important APIs/types/functions: `mvebu_get_soc_id`, `get_soc_id_by_pci`, `mvebu_soc_id_init`, and `mvebu_soc_device` are the main routines. Globals cache `soc_dev_id` and `soc_rev` after early init.

Control flow, state, and persistence: Control flow prefers `mvebu_system_controller_get_soc_id`; if unavailable on Armada 370/XP it scans PCI buses/devices, filters vendor/class, and reads revision. `postcore_initcall` formats IDs and creates sysfs SoC metadata.

Dependencies and integration points: `mvebu_get_soc_id`, `get_soc_id_by_pci`, `mvebu_soc_id_init`, and `mvebu_soc_device` are the main routines. Globals cache `soc_dev_id` and `soc_rev` after early init. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include PCI, DT machine compatibility, system-controller code, and `sys_soc`. Risks are absent PCI enumeration at early init, incorrect fallback on unsupported machines, and `-EINVAL` cached IDs suppressing soc registration. Test sysfs SoC attributes on Armada 370/XP and newer system-controller platforms.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 175 lines, 4070 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.c -->
