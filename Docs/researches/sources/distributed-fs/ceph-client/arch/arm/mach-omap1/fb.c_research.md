<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/fb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/fb.c

Purpose: OMAP framebuffer platform-device registration. It stores board-provided LCD configuration and registers `omapfb` only if a board called `omapfb_set_lcd_config`.

Important APIs/types/functions: The main API is `omapfb_set_lcd_config`; init is `omap_init_fb` at `arch_initcall`.

Control flow, state, and persistence: State includes `omapfb_lcd_configured`, `omapfb_config`, a 32-bit DMA mask, and LCD/SOSSI IRQ resources. Boards persist their LCD controller name through the copied config.

Dependencies and integration points: The main API is `omapfb_set_lcd_config`; init is `omap_init_fb` at `arch_initcall`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include `CONFIG_FB_OMAP`, omapfb platform data, LCD IRQ definitions, and board files. Risks are late/missing board calls causing no framebuffer device and shallow-copy assumptions for config fields. Test boards with LCD, no-LCD builds, IRQ resources, and DMA mask behavior.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 84 lines, 1728 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/fb.c -->
