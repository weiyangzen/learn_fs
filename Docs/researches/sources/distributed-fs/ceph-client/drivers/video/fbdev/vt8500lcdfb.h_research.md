<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.h

Purpose: Private header for the VT8500 LCD fbdev driver, defining the driver state container and supported bits-per-pixel hardware code mapping.

Important APIs/types/functions: `struct vt8500lcd_info` embeds `struct fb_info`, MMIO `regbase`, coherent palette CPU/physical address and size, and a waitqueue used for vsync waits. `bpp_values[]` maps hardware bpp selector indices to supported bpp values: 1, 2, 4, 8, 12, 16, 18, and 24.

Control flow and state: No standalone flow. `vt8500lcdfb.c` uses `container_of()` to recover this structure from `fb_info` and stores all persistent per-device runtime state here.

Dependencies and integration points: Relies on fbdev, I/O memory, DMA address, and waitqueue types included by the `.c` before this header. Risks include defining a non-const `static int bpp_values[]` in a header, no include guard, and header dependence on prior includes. Test signals are compile coverage, bpp selector mapping in `vt8500lcd_set_par()`, and static-analysis warnings for header-defined mutable data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vt8500lcdfb.h -->
