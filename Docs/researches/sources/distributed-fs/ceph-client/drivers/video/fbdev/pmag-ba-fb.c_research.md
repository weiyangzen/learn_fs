## sources/distributed-fs/ceph-client/drivers/video/fbdev/pmag-ba-fb.c

Purpose: this TurboChannel fbdev driver supports DEC PMAG-BA color framebuffer cards. It exposes a fixed 1024x864 8-bpp pseudocolor framebuffer, maps Bt459 RAMDAC registers and framebuffer memory, programs palette entries, and disables the hardware cursor at probe.

Important APIs/types/functions: `struct pmagbafb_par` holds MMIO and DAC pointers. `pmagbafb_defined` and `pmagbafb_fix` define fixed geometry, timing, 1 MiB framebuffer, 1024-byte line length, and pseudocolor visual. `dac_write()`/`dac_read()` access sparse Bt459 registers. `pmagbafb_setcolreg()` writes 8-bit RGB values into the Bt459 cmap. `pmagbafb_erase_cursor()` writes the cursor control register to disable it. Lifecycle functions are `pmagbafb_probe()` and `pmagbafb_remove()`.

Control flow: init registers the TC driver unless disabled by boot options. Probe allocates `fb_info`, allocates a 256-entry cmap, sets fbops/fix/var, reserves the full TC resource, maps MMIO, derives the Bt459 pointer, maps the framebuffer, sets `screen_size`, erases the cursor, registers fbdev, grabs a device reference, and logs. Remove reverses those operations, including cmap deallocation.

State and persistence behavior: palette state is in Bt459 RAMDAC registers and fbdev cmap memory. Cursor is simply disabled; no driver cursor state is tracked. Geometry is fixed and not recalculated at runtime. No persistent storage is used.

Dependencies and integration points: depends on TurboChannel core, fbdev default IOMEM ops, Linux resource/ioremap APIs, and `<video/pmag-ba-fb.h>` offsets/constants for Bt459 and framebuffer layout. Matching uses TC strings `DEC` and `PMAG-BA`.

Risks: fixed timing/geometry means no mode validation or runtime mode changes. Sparse register addressing divides offsets by four; wrong constants would hit wrong DAC registers. Palette writes return `1` for out-of-range, matching old fbdev convention but not a negative errno. Cursor is disabled but no fb_cursor callback is provided.

Test signals: probe on a PMAG-BA TC device, cmap allocation failure, palette programming through fbcon or `fbset`, framebuffer mmap/default ops, cursor remains hidden, resource cleanup on each failure path, and remove after registration.
