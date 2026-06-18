<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/nettel.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/nettel.c

Purpose: map driver for SnapGear/SecureEdge/NETtel x86 boards using AMD and optional Intel flash behind AMD SC520 PAR windows.

Important APIs, types, and functions: `nettel_amd_map`, optional `nettel_intel_map`, partition arrays for AMD and Intel layouts, `nettel_init()`, `nettel_cleanup()`, and optional `nettel_reboot_notifier()` for Intel CFI reset-to-read mode.

Control flow: init maps SC520 MMCR, programs CPU clock, manipulates PAR registers to probe AMD boot flash first, then, when `CONFIG_MTD_CFI_INTELEXT` is enabled, determines Intel boot/kernel flash layout, remaps PARs to detected sizes, reprobes combined Intel chips, adjusts partitions based on AMD-vs-Intel boot, registers Intel then AMD MTDs, and registers reboot notifier. Cleanup unregisters notifier and MTDs, destroys maps, and unmaps MMCR/flash windows.

State and persistence: persistent state is board flash contents and static partition data. Runtime state includes MMCR mapping, PAR register programming, AMD/Intel MTD pointers, and reboot notifier state.

Dependencies and integration points: uses SC520 MMCR/PAR hardware, JEDEC probe for AMD, CFI Intel extended command support, MTD partition registration, reboot notifier, and root device environment indirectly through board layout.

Risks: direct PAR and cache flush manipulation is platform-sensitive. Partition sizing is adjusted at runtime and must preserve BIOS regions. Error paths are complex and can leave partially changed PARs. Test signals are AMD-only and Intel+AMD layouts, reboot reset-to-read behavior, partition count adjustments, and cleanup after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/nettel.c -->
