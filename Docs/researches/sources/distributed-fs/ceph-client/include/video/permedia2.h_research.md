# sources/distributed-fs/ceph-client/include/video/permedia2.h

## Purpose
`permedia2.h` defines register offsets, RAMDAC indexed registers, flags, constants, and chip type identifiers for the 3Dlabs Permedia2 framebuffer driver.

## Important APIs, Types, and Functions
Constants include reference/max pixel clocks, register aperture size, and `PM2TAG(r)` for FIFO tags. Register groups cover reset/FIFO/aperture/config, memory control, output FIFO, screen timing, RAMDAC palette/cursor/indexed registers, rasterizer/render/scissor/texture/framebuffer/local-buffer/YUV/statistics/sync paths, and Permedia2V-specific RAMDAC extensions. Field macros cover render primitive/fast fill/texture/sync bits, PLL lock/reset, VGA/video enable, RAMDAC palette width/pixel formats, sync polarities, framebuffer read/write enables, texture sizes, delta order, memory bank count, aperture swap modes, and cursor mode. `pm2type_t` distinguishes Permedia2 and Permedia2V.

## Control Flow
The framebuffer driver probes the chip type, maps the register aperture, programs RAMDAC clocks and pixel format, writes screen timing and video enable registers, sets palette/cursor state, and may use render/framebuffer registers for fills or synchronization. `PM2TAG()` supports tagged FIFO command emission.

## State and Persistence Behavior
The header names hardware registers only. Runtime state includes programmed mode timing, RAMDAC state, cursor palette/pattern, framebuffer masks, and render engine configuration held in the device.

## Dependencies and Integration Points
It integrates fbdev mode setting and acceleration with Permedia2/Permedia2V MMIO and RAMDAC programming. It assumes Linux fixed-width integer types in consuming code.

## Risks and Test Signals
Risks include using Permedia2V extensions on base hardware, incorrect RAMDAC indexed register access, PLL lock handling, FIFO tag mistakes, and pixel-format/sync-polarity mismatches. Test signals include mode setting near clock limits, palette/cursor operations, render sync/fill, FIFO-space handling, Permedia2 vs Permedia2V probe paths, and register-offset audit against hardware specs.
