# sources/distributed-fs/ceph-client/drivers/video/fbdev/bw2.c

## Purpose
`bw2.c` is the Open Firmware/platform fbdev driver for Sun BWTWO monochrome framebuffers. It maps the one-bit framebuffer and BWTWO control registers, initializes monitor timing when firmware did not provide dimensions, and implements blanking plus SBUS mmap/ioctl compatibility.

## Important APIs, Types, and Functions
Key types are `struct bw2_regs`, `struct bt_regs`, and `struct bw2_par`. fbdev operations are supplied through `bw2_ops`, especially `bw2_blank()`, `bw2_sbusfb_mmap()`, and `bw2_sbusfb_ioctl()`. `bw2_do_default_mode()` chooses timing register tables based on status register monitor/type bits, and `bw2_init_fix()` fills fixed fb metadata.

## Control Flow
`bw2_probe()` allocates `fb_info`, fills var from OF properties, maps registers at `BWTWO_REGISTER_OFFSET`, optionally programs default timing, maps framebuffer RAM, unblanks video, initializes fix info, registers the framebuffer, and stores driver data. Removal unregisters and unmaps resources. Module init skips registration if `bw2fb` options disable the driver.

## State and Persistence
Per-device state includes a spinlock, mapped register pointer, blanked flag, and SBUS IO-space identifier. Hardware state includes timing registers, control video enable bit, and framebuffer RAM. No colormap is involved because the device is mono.

## Dependencies and Integration Points
The file depends on platform OF resources, `sbuslib.h` helpers, `asm/fbio.h` compatibility constants, and `sbus_readb()/sbus_writeb()` accessors. It presents Sun fbio-compatible mmap/ioctl behavior through `sbusfb_mmap_helper()` and `sbusfb_ioctl_helper()`.

## Risks and Edge Cases
Default timing depends on status bits and hard-coded tables; unknown monitor IDs fail probe. `BWTWO_SR_ID_NOCONN` returns success without programming timing, leaving behavior to firmware. The driver assumes resource 0 contains both framebuffer and registers at fixed offsets.

## Test Signals
Expected signals are successful OF match on `bwtwo`, correct mono visual and line length, blank/unblank toggling the video bit, mmap of the one-bit framebuffer through SBUS offsets, fbio type `FBTYPE_SUN2BW`, and correct default timing on ECL, analog, multisync, and 1600x1280 displays.
