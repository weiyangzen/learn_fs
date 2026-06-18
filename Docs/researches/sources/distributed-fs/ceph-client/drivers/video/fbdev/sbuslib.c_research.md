# sources/distributed-fs/ceph-client/drivers/video/fbdev/sbuslib.c

Purpose: helper library for SPARC SBUS framebuffer drivers. It provides common fb var initialization from Open Firmware properties, mmap mapping through SBUS physical/IOSPACE descriptors, native SPARC fb ioctls, and compat ioctl translation for 32-bit user space.

Important APIs/types/functions: exported helpers are `sbusfb_fill_var`, `sbusfb_mmap_helper`, `sbusfb_ioctl_helper`, and, under CONFIG_COMPAT, `sbusfb_compat_ioctl`. `sbusfb_mmapsize` interprets positive map sizes, `SBUS_MMAP_EMPTY`, and negative framebuffer-size multipliers. The ioctl helper handles `FBIOGTYPE`, `FBIOPUTCMAP_SPARC`, and `FBIOGETCMAP_SPARC`.

Control flow: `sbusfb_fill_var` zeroes var and fills dimensions from OF `width`/`height` properties with 1152x900 defaults. `sbusfb_mmap_helper` validates shared mapping, computes requested offset, marks the VMA decrypted and noncached, walks requested pages, finds matching map entries by virtual offset, computes SBUS PFNs with `MK_IOSPACE_PFN`, and remaps each segment. Native colormap ioctls copy index/count/user pointers, convert between 8-bit SPARC cmap components and fbdev 16-bit components, and call `fb_set_cmap` or copy from `info->cmap`. Compat ioctl either forwards simple commands to the driver's native ioctl or translates 32-bit cmap structures.

State and persistence: no private persistent state. It reads OF properties, uses caller-owned map tables and fb_info cmap state, and mutates user-visible mappings or color maps through core fbdev helpers.

Dependencies and integration: used by SBUS fbdev drivers via exported symbols and the `FB_DEFAULT_SBUS_OPS` macros in `sbuslib.h`. Depends on SPARC fb ioctl definitions from `asm/fbio.h`, Open Firmware property access, memory remapping primitives, user access helpers, and CONFIG_COMPAT for 32-bit translations.

Risks: mmap silently skips pages that do not match any map entry and still returns success if no remap fails, so callers must provide complete maps. The `FBIOGTYPE` path writes `fb_cmsize` twice, first zero and then `fb_size`, which looks intentional or historical but is surprising. User pointer validation is per-access. Map size arithmetic depends on sentinel values and negative multipliers.

Test signals: SBUS framebuffer mmap with multiple map entries, unmatched offsets, invalid non-shared VMAs, native SPARC cmap get/put bounds checks, compat cmap get/put from 32-bit processes, and exported-symbol build coverage for CONFIG_COMPAT on and off.
