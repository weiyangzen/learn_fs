<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/grvga.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/grvga.c

Purpose: implements an fbdev platform driver for Aeroflex Gaisler GRLIB SVGACTRL framebuffer hardware.

Important APIs, types, and functions: `struct grvga_regs` mirrors controller MMIO registers for status, timing, framebuffer position, clock vectors, and CLUT. `struct grvga_par` stores the mapped registers, pseudo-palette, selected clock, and whether framebuffer memory was driver-allocated. `grvga_check_var()` normalizes bpp to 8/16/24/32, enforces memory limits, validates the requested pixclock against hardware clock vectors, and sets color fields. `grvga_set_par()` writes timing registers and status bits. `grvga_setcolreg()` writes hardware CLUT for pseudocolor or pseudo-palette for truecolor. `grvga_pan_display()` writes aligned base address. `grvga_parse_custom()` parses a ten-field custom timing string. `grvga_probe()` parses boot options, maps registers, allocates cmap, finds/parses mode, maps supplied framebuffer memory or allocates pages, reserves pages for mmap, clears memory, and registers fbdev.

Control flow: platform probe gets `grvga` fb options, configures `fb_info`, maps resources, chooses mode, prepares framebuffer memory, registers fbdev, then writes the framebuffer base and enables the controller. Runtime callbacks validate mode, program timing/status registers, update CLUT/pseudo-palette, and pan by changing `fb_pos`.

State and persistence: `grvga_par` stores register mapping and clock selection. Framebuffer memory may be externally supplied via `addr` or allocated by the driver and DMA-mapped. For allocated memory, pages are marked reserved for mmap and `fb_alloced` controls cleanup.

Dependencies and integration points: depends on platform resources from OF, fbdev, DMA mapping, boot option string `grvga`, and GRLIB/SVGACTRL clock-vector hardware. OF matching uses names `GAISLER_SVGACTRL` and `01_063`.

Risks: `grvga_check_var()` switches on `info->var.bits_per_pixel` instead of the normalized `var->bits_per_pixel`, which can apply stale color-field logic. Allocated framebuffer cleanup uses `kfree()` on memory allocated with `__get_free_pages()`, rather than `free_pages()`, in this source. DMA mapping is not explicitly unmapped in remove. Custom parsing accepts sparse invalid fields until downstream validation.

Test signals: mode selection for each built-in mode and custom mode, pixclock rejection when not in clock vectors, supplied versus allocated framebuffer paths, mmap of reserved pages, y-pan base alignment, CLUT writes in 8 bpp and pseudo-palette writes in truecolor, and remove cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/grvga.c -->
