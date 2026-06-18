# sources/distributed-fs/ceph-client/drivers/video/fbdev/xilinxfb.c

Purpose: framebuffer driver for Xilinx TFT LCD controller variants. It handles a simple fixed-format truecolor controller with framebuffer base and control registers, supporting OF-provided dimensions, BUS or PPC DCR register access, optional screen rotation, and either supplied or DMA-allocated framebuffer memory.

Important APIs, types, and functions: `struct xilinxfb_platform_data` defines resolution, virtual resolution, physical size, rotation, and optional fb physical address. `struct xilinxfb_drvdata` embeds `fb_info`, register access state, framebuffer allocation state, flags, default control value, and pseudo-palette. Key functions are `xilinx_fb_out32`, `xilinx_fb_in32`, `xilinx_fb_setcolreg`, `xilinx_fb_blank`, `xilinxfb_assign`, `xilinxfb_release`, `xilinxfb_of_probe`, and `xilinxfb_of_remove`.

Control flow: OF probe starts from default 640x480 visible, 1024x480 virtual geometry, allocates drvdata, determines BUS versus DCR access from `xlnx,dcr-splb-slave-if`, maps registers or DCR host, parses optional `phys-size`, `resolution`, `virtual-resolution`, and `rotate-display`, then delegates to `xilinxfb_assign`. Assignment maps/allocates framebuffer memory, clears it, writes framebuffer base, detects little-endian register access if the readback differs, enables display and rotation, fills `fb_info`, allocates cmap, and registers the framebuffer. Blank writes control enable or zero.

State and persistence: runtime state is drvdata, hardware control registers, pseudo-palette, and framebuffer memory. DMA-allocated memory is freed on release; caller-provided physical memory is ioremapped and unmapped only. No persistent storage exists.

Dependencies and integration points: depends on platform/OF, fbdev default IOMEM ops, DMA coherent allocation, optional PPC DCR APIs, and Xilinx compatible strings for XPS/PLB TFT/DVI controllers.

Risks: hardware format is effectively fixed at 32 bpp with 24 useful color bits; mode validation/set_par are absent, so users cannot safely change modes. If register endianness readback fails for reasons other than byte order, the driver switches access mode. Supplied `fb_phys` is trusted. DCR path only exists under `CONFIG_PPC_DCR`. Error paths must disable the display and free the right memory kind.

Test signals: build BUS and PPC DCR configurations; boot with each supported compatible; validate OF geometry parsing, big/little-endian MMIO access, blank/unblank, pseudo-palette color rendering, rotation bit, DMA allocation and external framebuffer paths, and remove cleanup.
