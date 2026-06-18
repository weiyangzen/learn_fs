## sources/distributed-fs/ceph-client/drivers/video/fbdev/pmag-aa-fb.c

Purpose: this TurboChannel fbdev driver supports DEC PMAG-AA monochrome framebuffer cards. It maps the Bt455 RAMDAC, Bt431 cursor generator, and framebuffer memory, initializes a 1-bit effective monochrome display exposed as 8 bpp, implements blanking through the colormap, and supports hardware cursor operations.

Important APIs/types/functions: `struct aafb_par` stores the MMIO base and typed Bt455/Bt431 register pointers. `aafb_defined` and `aafb_fix` define 1280x1024 display geometry, 2048-byte virtual line stride, grayscale/pseudocolor characteristics, mono visual, and resource lengths. `aafb_cursor()` validates cursor size and delegates position, cmap, shape/image, erase, and enable operations to Bt431/Bt455 helpers. `aafb_blank()` writes black or white into colormap entry 1. Probe/remove are `pmagaafb_probe()` and `pmagaafb_remove()`.

Control flow: init registers a TC driver unless boot options disable it. Probe allocates `fb_info`, sets fbops/fix/var, reserves the whole TC slot resource, maps the MMIO window from Bt455 through before framebuffer memory, derives Bt455 and Bt431 pointers, maps framebuffer memory, initializes the two-entry monochrome colormap, erases and initializes the cursor generator, registers fbdev, takes a device reference, and logs the device. Remove drops the reference, unregisters, unmaps framebuffer/MMIO, releases the TC resource, and releases `fb_info`.

State and persistence behavior: state is hardware register contents plus `fb_info`; no disk persistence exists. The cursor image lives in Bt431 hardware. Blank state is represented by a RAMDAC colormap entry rather than a separate driver flag.

Dependencies and integration points: depends on the TurboChannel bus, fbdev default I/O-memory operations, Linux IO mapping/resource APIs, and local `bt455.h`/`bt431.h` helper APIs. Matching uses TC vendor/product strings `DEC` and `PMAG-AA`.

Risks: pointer arithmetic on `void __iomem *` is compiler-extension style but common in this tree. There is no cmap allocation because the monochrome DAC is managed directly, so fbdev colormap expectations are narrow. Cursor color maps logical fg/bg to 0x0/0xf only. The framebuffer is exposed as 8 bpp though only the least significant bit is meaningful.

Test signals: TC probe/remove, MMIO/framebuffer map failures, fbcon monochrome rendering, blank/unblank toggling colormap entry 1, cursor size rejection over `BT431_CURSOR_SIZE`, cursor position/cmap/shape updates, and resource release after failed register_framebuffer.
