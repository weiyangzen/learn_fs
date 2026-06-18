# sources/distributed-fs/ceph-client/drivers/video/fbdev/sstfb.c

## Purpose
`sstfb.c` is a PCI fbdev driver for 3dfx Voodoo Graphics and Voodoo2 boards. It maps the Voodoo MMIO and linear framebuffer windows, detects attached RAMDAC type, programs graphics/video PLLs, validates and applies 16 bpp display modes, manages VGA pass-through, detects framebuffer memory size, exposes basic fbdev IOMEM operations and a small ioctl/sysfs control surface, and shuts the board down on removal.

## Important APIs, types, and functions
- Module options and hardware tables: `vgapass`, `mem`, `clipping`, `gfxclk`, `slowpci`, `mode_option`, `voodoo_spec[]`, and `dacs[]`.
- MMIO/DAC helpers: `__sst_read()`, `__sst_write()`, `__sst_set_bits()`, `__sst_unset_bits()`, `__sst_wait_idle()`, `__sst_dac_read()`, `__sst_dac_write()`, `__dac_i_read()`, and `__dac_i_write()`.
- Timing and mode functions: `sst_calc_pll()`, `sstfb_check_var()`, `sstfb_set_par()`, `sstfb_setcolreg()`, and `sstfb_clear_screen()`.
- VGA pass-through and userspace controls: `sstfb_setvgapass()`, `store_vgapass()`, `show_vgapass()`, and `sstfb_ioctl()`.
- Hardware detection/init: `sst_get_memsize()`, `sst_detect_att()`, `sst_detect_ti()`, `sst_detect_ics()`, `sst_set_pll_att_ti()`, `sst_set_pll_ics()`, `sst_set_vidmod_att_ti()`, `sst_set_vidmod_ics()`, `sst_detect_dactype()`, `sst_init()`, and `sst_shutdown()`.
- PCI lifecycle: `sstfb_probe()`, `sstfb_remove()`, `sstfb_init()`, `sstfb_exit()`, and `sstfb_id_tbl`.

## Control flow
Module init parses `video=sstfb:` options, updates global behavior flags and initial mode string, and registers the PCI driver. Probe removes conflicting firmware apertures, enables PCI, allocates `fb_info` with `struct sstfb_par`, records Voodoo1/Voodoo2 type, reserves and maps the 4 MiB MMIO and framebuffer windows, runs `sst_init()` to reset the board, remap DAC access, detect the DAC, set the graphics clock, initialize FBI registers, and enable the video clock. It then detects usable framebuffer size, selects and validates a mode through `fb_find_mode()`/`sstfb_check_var()`, programs the mode with `sstfb_set_par()`, allocates a colormap, registers fbdev, clears the screen, and optionally creates the `vgapass` sysfs file. Runtime `set_par` resets video/FBI/FIFO, writes timing registers, programs the DAC video mode and PLL, restores FBI registers, configures tile counts, enables DRAM refresh, selects 565 LFB mode, and optionally enables clipping.

## State and persistence behavior
Private state in `struct sstfb_par` comes from `video/sstfb.h` and includes PCI device, board type/revision, MMIO base, current PLL timing, DAC switch table, palette, VGA pass-through state, and computed timing/tile fields. Global module parameters persist policy across devices. `sst_get_memsize()` writes test patterns into framebuffer memory to infer 1/2/4 MiB unless the `mem` option forces a value. The pseudo-palette stores up to 16 truecolor entries; no hardware CLUT is programmed for 16 bpp. Remove calls `sst_shutdown()` to reset video/gfx/fifo, drop DRAM refresh, set a low graphics clock, enable VGA pass-through, disable video clock, then unmaps resources and unregisters fbdev.

## Dependencies and integration points
The driver depends on PCI IDs for `PCI_DEVICE_ID_3DFX_VOODOO` and `PCI_DEVICE_ID_3DFX_VOODOO2`, aperture removal, fbdev IOMEM helpers, mode database, usercopy, sysfs under `CONFIG_FB_DEVICE`, and register definitions/types from `video/sstfb.h`. It exposes ioctls `SSTFB_SET_VGAPASS` and `SSTFB_GET_VGAPASS`, module options for memory size/VGA pass-through/clipping/gfx clock/PCI speed/mode, and a sysfs `vgapass` attribute.

## Risks
`__sst_wait_idle()` is an unbounded busy loop; stuck hardware can hang the CPU. Failure during `sst_init()` can leave hardware in a reset/remapped state, which the comments acknowledge. Only 16 bpp is supported despite comments about legacy 24/32 bpp, and Voodoo1 rejects interlace/doublescan. Memory detection writes directly to framebuffer offsets and may disturb visible contents. Forced `gfxclk` is explicitly dangerous if out of spec. Resource cleanup on probe failure returns `-ENXIO` regardless of original failure. Clipping disabled can make offscreen writes wrap unpredictably. There is no suspend/resume support.

## Test signals
Relevant tests include Voodoo1 and Voodoo2 probe on known DAC variants (TI, AT&T, ICS), invalid DAC detection handling, PLL calculation across default and selected modes, rejection of unsupported bpp/timings/resolutions, Voodoo2 interlace/doublescan handling, memory-size autodetect and forced `mem`, `vgapass` ioctl/sysfs/module option behavior, clipping on/off framebuffer writes near screen boundaries, big-endian LFB swizzle, failed resource-map cleanup, remove shutdown leaving VGA pass-through usable, and stress around hardware idle waits.
