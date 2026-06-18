# sources/distributed-fs/ceph-client/include/video/pm3fb.h

## Purpose
`pm3fb.h` is the register and bitfield definition header for the 3Dlabs GLINT Permedia3 framebuffer driver. It covers control/status, memory, video timing, overlay, RAMDAC, 3D/render, framebuffer/local-buffer, texture, 2D setup, alias registers, ioctl, FIFO, and clock limits.

## Important APIs, Types, and Functions
The file defines macros only. Major groups include `PM3ResetStatus` and control/status registers, aperture mode fields, memory control, screen timing and `PM3VideoControl`, overlay mode/geometry/scaling registers, direct and indexed RAMDAC registers, cursor and overlay RAMDAC controls, D/K/M clock setup and lock fields, framebuffer read/write buffer registers, local-buffer read/write formats, logical operation, LUT, pixel-size, render, rasterizer, scissor, texture, window, 2D config/render/glyph/rectangle registers, fill aliases, sync/statistics/filter registers, `PM3FBIO_RESETCHIP`, `PM3_FIFO_SIZE`, `PM3_REGS_SIZE`, and `PM3_MAX_PIXCLOCK`.

## Control Flow
The framebuffer driver maps registers, programs memory/aperture and clock/RAMDAC state, sets screen timing and video enable bits, configures palette/cursor/overlay, uses framebuffer/render/2D setup registers for accelerated operations, waits for sync/completion, and may expose reset through the ioctl constant.

## State and Persistence Behavior
All state represented is hardware state: clocks, display timing, RAMDAC/cursor/palette, overlay buffers/scaling, render and framebuffer modes, local-buffer settings, and FIFO/sync state. It persists until reset, mode change, or power transition.

## Dependencies and Integration Points
It integrates the pm3fb driver with PCI/MMIO register access, fbdev mode setting, RAMDAC programming, 2D acceleration, overlay support, and legacy ioctl userspace.

## Risks and Test Signals
Risks include wrong bitfield composition macros, FIFO overflow due to missing space checks, pixel clock programming beyond `PM3_MAX_PIXCLOCK`, overlay scaling division edge cases, reset ioctl ABI issues, and confusion between direct/indirect RAMDAC registers. Test signals include mode-setting across depths, palette/cursor, accelerated rectangles/glyphs/blits, overlay enable/scale/color formats, sync/fifo tests, reset ioctl behavior, and register audit against Permedia3 documentation.
