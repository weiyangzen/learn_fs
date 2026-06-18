# sources/distributed-fs/ceph-client/include/video/kyro.h

## Purpose
`kyro.h` defines private framebuffer state and user ioctl payloads for the STMicroelectronics/PowerVR Kyro framebuffer driver, especially display timing and overlay/video-mode operations.

## Important APIs, Types, and Functions
`struct kyrofb_info` stores MMIO base, a 16-entry pseudo-palette, horizontal/vertical timing fields, resolution, refresh, pixel and horizontal clocks, pixel depth, and write-combine cookie. Ioctls use magic `k` and include overlay create, viewport set, video mode set, UV stride, overlay offset, and stride commands. Payload structs are `overlay_create`, `overlay_viewport_set`, and `set_video_mode`.

## Control Flow
The driver populates `kyrofb_info`, programs timing and palette data into hardware, and handles user ioctls by creating/configuring overlays or changing mode-related values. User-space passes simple width/height/linear/viewport/depth records through ioctl.

## State and Persistence Behavior
State is per-framebuffer runtime state plus hardware overlay/mode registers. The pseudo-palette is cached in software for console/framebuffer use; no persistent configuration is stored by this header.

## Dependencies and Integration Points
It integrates framebuffer driver internals, PCI/MMIO mapping, write-combining setup, and legacy user-space overlay ioctl ABI. It expects Linux ioctl encoding and fixed-width types from included kernel headers.

## Risks and Test Signals
Risks include ioctl ABI compatibility, unchecked dimensions or linear flags, stale write-combine mappings, and mismatch between cached timing fields and programmed hardware. Test signals include fbdev mode changes, palette updates, overlay creation/viewport ioctls from 32-bit and native userspace, stride/offset validation, and unload cleanup of MMIO/write-combine resources.
