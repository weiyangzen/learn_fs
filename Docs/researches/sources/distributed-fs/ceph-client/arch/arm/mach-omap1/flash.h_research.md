<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.h

Purpose: Header for OMAP1 flash VPP support. It declares the helper used by board physmap flash data.

Important APIs/types/functions: The API is `omap1_set_vpp(struct platform_device *pdev, int enable)`.

Control flow, state, and persistence: No state exists in the header; hardware state is in EMIFS registers manipulated by `flash.c`.

Dependencies and integration points: The API is `omap1_set_vpp(struct platform_device *pdev, int enable)`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are missing declaration if flash support changes. Test compile of all board files using physmap flash.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 14 lines, 255 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.h -->
