# sources/distributed-fs/ceph-client/drivers/video/fbdev/asiliantfb.c

## Purpose
`asiliantfb.c` is a compact PCI framebuffer driver for Asiliant/Chips 69000-family display controllers, especially the 69030/69000 class. It maps the controller framebuffer/MMIO aperture, initializes indexed VGA and flat-panel registers, computes dot-clock PLL settings, supports 8/16/24bpp fbdev modes, and registers a legacy fbdev device.

## Important APIs, Types, and Functions
The driver uses `struct fb_info` directly, with a 16-entry pseudo-palette allocated as framebuffer private memory. Indexed register helpers `mm_write_xr`, `mm_write_fr`, `mm_write_cr`, `mm_write_gr`, `mm_write_sr`, and `mm_write_ar` write Asiliant/VGA register banks through MMIO offsets under `mmio_base = screen_base + 0x400000`.

Mode and color entry points are `asiliantfb_check_var()`, `asiliantfb_set_par()`, and `asiliantfb_setcolreg()`. `asiliant_calc_dclk2()` computes PLL divisor and m/n fields from `pixclock` using `Fref = 14318180`. `asiliant_set_timing()` programs CRT timing, line width, panel/CRT selector, and misc output. Static register tables `chips_init_sr/gr/ar/cr/fr/xr` are applied by `chips_hw_init()`. PCI lifecycle is `asiliantfb_pci_init()` and `asiliantfb_remove()`.

## Control Flow
Module init checks `fb_modesetting_disabled("asiliantfb")`, honors `fb_get_options("asiliantfb", NULL)`, and registers a PCI driver for `PCI_VENDOR_ID_CT` and `PCI_DEVICE_ID_CT_69000`. Probe removes conflicting aperture users, validates BAR0 memory, reserves the memory region, allocates `fb_info`, maps 8 MiB of the aperture, writes PCI command/config bits directly, performs a small MMIO output write, initializes fb defaults, allocates a 256-entry colormap, registers the framebuffer, initializes hardware register tables, and stores driver data.

When fbdev requests a mode, `check_var` validates dot clock limits and normalizes virtual resolution to the visible resolution. It supports 8bpp pseudocolor, 16bpp RGB555/RGB565 based on red offset, and 24bpp RGB888. `set_par` computes DCLK2 PLL values, programs pixel pipeline mode, line length, visual type, clock registers, and timing registers. Palette writes program hardware DAC entries and update the pseudo-palette for the first 16 truecolor entries.

## State and Persistence
The driver keeps minimal software state: fb_info, colormap, pseudo-palette, and the MMIO mapping. Hardware register state persists in the display controller until reset or driver reprogramming. It has no suspend/resume path and no disk persistence.

## Dependencies and Integration Points
Dependencies include PCI, fbdev IOMEM operations, aperture conflict removal, MMIO accessors, memory resource reservation, and legacy VGA-style indexed register behavior. User-space integration is the fbdev node; hardware integration is PCI BAR0 where both framebuffer and MMIO register windows are mapped.

## Risks and Edge Cases
Probe maps a fixed 8 MiB window while `fix.smem_len` is 2 MiB and the resource size is only validated for being nonzero; small or differently laid-out BARs could be overmapped. `pci_enable_device()` is not called, and the driver writes PCI config dword 4 directly instead of using PCI helpers, which is fragile across platforms. There is no power-management handling. `check_var` does not reject unsupported bpp values explicitly after handling 8/16/24, so an unsupported bpp may reach `set_par()` with incomplete color fields. Dot-clock calculation has no failure return if no valid m/n pair is found; best values start as `0xffffffff`, so invalid arithmetic would be dangerous if constraints are wrong. The code registers the framebuffer before `chips_hw_init()`, so users could theoretically observe an fb before hardware programming completes.

## Test Signals
Validation should include PCI probe/remove, BAR/resource-size sanity, aperture handoff from firmware fb, 640x480 default mode, 8bpp palette writes, RGB555 and RGB565 16bpp pseudo-palette, 24bpp truecolor, dot-clock limits below 3.125 MHz and above 220 MHz, mode timing changes between LCD/CRT selector paths, and failure cleanup for region reservation, ioremap, colormap allocation, and framebuffer registration.
