# sources/distributed-fs/ceph-client/drivers/video/fbdev/cyber2000fb.h

## Purpose
`cyber2000fb.h` is the CyberPro register and companion-module contract header.

## APIs And Control Flow
It defines MMIO layout, palette size, RAMDAC bits, VGA extension registers, capture/video/TV/bus-master registers, graphics coprocessor registers, chip IDs, and optional low-level debug output. `struct cyberpro_info` exposes device, I2C, register/fb, size, chip, IRQ, and opaque `cfb_info` pointer fields to related modules. It declares `cyber2000fb_enable_extregs()` and `cyber2000fb_disable_extregs()`.

## State, Dependencies, Integration, Risks
The header itself is mostly stateless constants, but it describes hardware state consumed by `cyber2000fb.c` and companion CyberPro modules. Risks are silent misprogramming from wrong constants and the fixed-size `debug_printf()` buffer in debug builds. Test signals are compile coverage with DDC/I2C users, acceleration register validation, RAMDAC mode checks, and extended-register bank access.
