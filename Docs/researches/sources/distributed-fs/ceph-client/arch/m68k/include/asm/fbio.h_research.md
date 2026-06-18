<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/fbio.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/fbio.h

## Purpose
This header defines Sun-style framebuffer ioctl ABI structures, type IDs, cursor/color-map/window-ID controls, and framebuffer memory-map offsets used by m68k Sun framebuffer drivers and compatible userspace.

## Important APIs, Types, And Functions
- `FBTYPE_*` constants identify many Sun framebuffer device classes.
- `struct fbtype`, `struct fbcmap`, `struct fbsattr`, `struct fbgattr`, `struct fbcursor`, `struct fbcurpos`, `struct fb_wid_alloc`, `struct fb_wid_item`, and `struct fb_wid_list` define ioctl payloads.
- Ioctls include `FBIOGTYPE`, `FBIOPUTCMAP`, `FBIOGETCMAP`, `FBIOSATTR`, `FBIOGATTR`, video on/off, cursor operations, and WID allocate/free/get/put.
- FFB, MDI, and LEO ioctl constants and CLUT structs define additional compatibility commands.
- Kernel-only offsets define CG6, CG3, TCX, and CG14 mmap/register regions.

## Control Flow
Userspace sends ioctls with these structures to framebuffer drivers. Drivers copy payloads, update hardware color maps/cursors/video state, return attributes, and interpret mmap offsets for device memory regions.

## State And Persistence Behavior
Persistent state is held by framebuffer hardware and drivers: color maps, cursor image/position, video enablement, WID allocations, gamma/CLUT state, and mapped framebuffer memory. The header defines ABI layout only.

## Dependencies And Integration Points
It depends on Linux compiler/types and ioctl encoding macros. It integrates with Sun3/m68k framebuffer drivers and legacy Sun framebuffer userspace interfaces.

## Risks And Edge Cases
This is a userspace ABI; structure layout and ioctl numbers are stable contracts. Some ioctl names are unsupported or historical but must remain compatible. 32-bit pointer fields and endian behavior matter for user ABI.

## Test Signals
Framebuffer ioctl tests for type query, color map get/put, cursor get/set/position, video enable/disable, mmap offsets, and legacy Sun fb tools validate compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/fbio.h -->
