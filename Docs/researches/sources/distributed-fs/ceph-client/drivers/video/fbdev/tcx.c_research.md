# sources/distributed-fs/ceph-client/drivers/video/fbdev/tcx.c

## Purpose
`tcx.c` is the SBUS/Open Firmware fbdev driver for Sun TCX framebuffers. It supports 8-bit and 24-bit TCX variants, Brooktree DAC palette programming, THC blanking, control-plane reset for 24-bit cards, legacy SBUS mmap offsets, and fbio ioctl compatibility.

## Important APIs, Types, and Functions
Important hardware structures are `struct tcx_tec`, `struct tcx_thc`, and `struct bt_regs`; private driver state is `struct tcx_par`. fbdev callbacks are `tcx_setcolreg()`, `tcx_blank()`, `tcx_pan_display()`, `tcx_sbusfb_mmap()`, and `tcx_sbusfb_ioctl()`. Setup/teardown helpers include `__tcx_set_control_plane()`, `tcx_reset()`, `tcx_init_fix()`, `tcx_unmap_regs()`, `tcx_probe()`, and `tcx_remove()`.

## Control Flow
`tcx_probe()` allocates `fb_info`, detects low-depth cards via `tcx-8-bit`, fills `var` from OF, maps TEC, THC, DAC, framebuffer RAM, and optionally the control plane, builds a per-device mmap table from OF resources, initializes DAC control registers, resets the control plane, unblanks video, allocates and installs a cmap, initializes fixed metadata, and registers fbdev. `tcx_pan_display()` is used as a reset hook. `tcx_blank()` manipulates THC video, hsync, and vsync bits. mmap/ioctl requests are delegated to SBUS helper functions with TCX-specific map and fb type data.

## State and Persistence
Per-device state stores mapped hardware blocks, the low-depth flag, blanked flag, SBUS iospace, and adjusted mmap map. Hardware state includes BT DAC registers, THC timing/blanking bits, cursor registers, control-plane contents, and framebuffer RAM. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on OF platform resources, SBUS accessors and `sbuslib.h`, `<asm/fbio.h>` legacy constants, fbdev cmap/mmap/ioctl infrastructure, and platform driver binding for `SUNW,tcx`.

## Risks and Edge Cases
`__tcx_set_control_plane()` iterates `info->fix.smem_len` u32 entries, which depends on the control-plane mapping size matching framebuffer bytes times four. Low-depth mode disables several mmap regions. The mmap resource index remapping is non-obvious. Blank powerdown does not add behavior beyond existing blank bits. Hardware cursor areas are exposed by mmap but not managed as fbdev cursor.

## Test Signals
Test 8-bit and 24-bit OF nodes, mmap offsets for RAM8BIT/RAM24BIT/control/DAC/THC, palette writes, pan-triggered reset, all blank states, fbio helper output, control-plane clearing on 24-bit cards, and remove-path unmapping/cmap cleanup.
