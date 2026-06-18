# sources/distributed-fs/ceph-client/drivers/video/fbdev/chipsfb.c

## Purpose
`chipsfb.c` is a PCI fbdev driver for the Chips & Technologies 65550 framebuffer, historically used on PowerBook-class systems. It programs VGA-style indexed registers through fixed I/O ports, maps the framebuffer aperture, supports 800x600 at 8 or 16 bpp, and optionally coordinates with PowerMac backlight support and PCI suspend/resume.

## Important APIs, Types, and Functions
Register macros `write_xr/read_xr`, `write_fr/read_fr`, `write_cr/read_cr`, `write_gr/read_gr`, `write_sr/read_sr`, and `write_ar/read_ar` wrap port I/O. fbdev callbacks are `chipsfb_check_var()`, `chipsfb_set_par()`, `chipsfb_setcolreg()`, and `chipsfb_blank()`. Hardware tables use `struct chips_init_reg`, applied by `chips_hw_init()`. Lifecycle functions are `chipsfb_pci_init()`, `chipsfb_remove()`, suspend/resume hooks, `chips_init()`, and `chipsfb_exit()`.

## Control Flow
`chipsfb_pci_init()` removes conflicting aperture drivers, enables PCI, validates BAR0 memory, allocates `fb_info`, requests BAR0, enables memory and I/O in PCI command register, optionally turns on PMac backlight, maps the aperture, initializes fb metadata and hardware registers, and registers the framebuffer. Mode setting rewrites line length and color-mode registers for 8-bit pseudocolor or 15/16-bit truecolor. Removal unregisters, unmaps, and releases the PCI region.

## State and Persistence
The driver keeps little per-device state beyond `fb_info`; hardware state is programmed into VGA/extension/flat-panel registers and RAMDAC palette ports. The fixed `chipsfb_fix` assumes 1MB of visible framebuffer memory, while mapping may cover 2MB. Suspend marks the fb suspended and relies on console lock coordination.

## Dependencies and Integration Points
Dependencies include PCI, aperture conflict handling, fbdev IOMEM ops, fixed legacy VGA I/O ports, optional `CONFIG_PMAC_BACKLIGHT`, and architecture-specific framebuffer mapping (`ioremap_wc()` on PPC). It binds PCI vendor/device IDs for CT 65550.

## Risks and Edge Cases
The code explicitly supports only one chip because fixed I/O ports are global. Memory-size detection is not implemented and the fix info assumes 1MB despite some systems having 2MB. `chipsfb_blank()` delegates to fbdev colormap blacking rather than powering down hardware. 16 bpp is programmed as 15-bit 555 color, which may surprise users expecting RGB565.

## Test Signals
Signals include successful bind to CT 65550, visible 800x600 output, palette writes in 8 bpp, correct pseudo/truecolor metadata after bpp changes, no conflict with aperture owners, PMac backlight activation where configured, suspend/resume console behavior, and clean removal with BAR release.
