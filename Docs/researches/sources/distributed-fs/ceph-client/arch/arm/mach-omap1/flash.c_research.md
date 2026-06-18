<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.c

Purpose: OMAP1 NOR flash VPP control helper. It toggles the EMIFS write-protect/VPP bit for physmap flash platform data.

Important APIs/types/functions: The only API is `omap1_set_vpp(struct platform_device *pdev, int enable)`.

Control flow, state, and persistence: State is the EMIFS_CONFIG hardware register. The helper reads, sets or clears `OMAP_EMIFS_CONFIG_WP`, then writes it back.

Dependencies and integration points: The only API is `omap1_set_vpp(struct platform_device *pdev, int enable)`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP1 register accessors, EMIFS definitions, and MTD/physmap board data. Risks are global EMIFS bit side effects across multiple flash devices and lack of locking. Test flash erase/write enable/disable on OSK, PalmTE, and SX1.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 26 lines, 440 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.c -->
