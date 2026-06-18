# sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb.c

## Purpose
`carminefb.c` is a PCI fbdev driver for Fujitsu Carmine devices. It initializes the GPU/DRAM controller, maps register and display-memory BARs, and exposes up to two independent 32-bit truecolor framebuffers, one per display.

## Important APIs, Types, and Functions
Key types are `struct carmine_hw`, `struct carmine_resolution`, and `struct carmine_fb`. fbdev callbacks are `carmine_check_var()`, `carmine_set_par()`, and `carmine_setcolreg()`. Hardware setup is divided between `init_hardware()`, `carmine_init_display_param()`, and `set_display_parameters()`. PCI lifecycle functions are `carminefb_probe()`, `carminefb_remove()`, `carminefb_init()`, and `carminefb_cleanup()`.

## Control Flow
Module init rejects disabled modesetting or no selected display, then registers the PCI driver. Probe removes conflicting aperture drivers, enables the PCI device, reserves and maps config and memory BARs, caps the large memory BAR to the two-display framebuffer requirement, runs DRAM/display initialization, allocates display 0 and/or display 1 framebuffers, and stores `struct carmine_hw` as PCI driver data. Mode setting validates against two built-in modes and writes display timing/layer registers when the mode changes.

## State and Persistence
Per-device state tracks mapped register memory, mapped screen memory, and up to two `fb_info` objects. Per-framebuffer state tracks display register base, screen offset, current/new mode, resolution table pointer, and pseudo-palette. Hardware state includes DRAM controller settings, display clock/output enable, layer origins, timing registers, and framebuffer memory contents.

## Dependencies and Integration Points
The driver depends on PCI, aperture conflict removal, fbdev IOMEM ops, `carminefb.h` DRAM defaults, and `carminefb_regs.h` offsets. Module parameters `fb_mode`, `fb_mode_str`, and `fb_displays` control initial mode/display selection. It binds Fujitsu vendor `0x10cf`, device `0x202b`.

## Risks and Edge Cases
Only 640x480 and 800x600 are supported. DRAM timing defaults are compile-time configuration dependent and board-sensitive. `carmine_setcolreg()` stores big-endian pseudo-palette entries, so endian behavior must match hardware and fbdev expectations. Probe uses global `carminefb_fix`, so concurrent devices would share mutable fix fields. Cleanup comments include a typo about display selection but logic chooses an existing fb for BAR release.

## Test Signals
Signals include correct PCI bind, BAR reservation/mapping, visible 32-bit output on selected displays, correct behavior for both module mode-selection paths, successful rejection of unsupported modes, pseudo-palette color correctness on big/little endian hosts, and clean remove after one-display and two-display configurations.
