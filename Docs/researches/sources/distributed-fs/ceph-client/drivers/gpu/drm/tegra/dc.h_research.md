# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dc.h

## Purpose
`dc.h` is the shared display-controller contract for Tegra DRM. It defines the CRTC state, display-controller instance state, SoC capability descriptions, window programming data, public DC helper prototypes, RGB helper prototypes, and the display-controller register/bitfield map used by `dc.c` and output drivers.

## Important APIs, Types, and Definitions
`struct tegra_dc_state` extends `drm_crtc_state` with the selected parent clock, pixel clock, shift-clock divider, and a bitmask of planes that need update/activate requests. `struct tegra_dc_stats` stores frame, vblank, underflow, and overflow counters for the current active interval and total device lifetime. `struct tegra_dc_soc_info` describes per-generation feature support such as cursor, block-linear layout, sector layout, legacy blending, powergate, coupled PM, NVdisplay, pitch alignment, window groups, supported formats/modifiers, filter limitations, and PLL availability.

`struct tegra_dc` is the device object embedded around a host1x client and DRM CRTC. It stores syncpoint, device, pipe, clock/reset/register/IRQ handles, RGB output, stats, debugfs files, SoC info, and OPP availability. `struct tegra_dc_window` is the transient plane programming payload consumed by `dc.c`; it carries source/destination rectangles, bpp, strides, base addresses, zpos, reflection flags, tiling, hardware color format, and byte swap.

The header provides inline register accessors `tegra_dc_writel()` and `tegra_dc_readl()` with trace hooks, and conversion helpers from DRM/host1x objects to Tegra objects.

## Control Flow Role
The header itself has no runtime control flow, but it encodes the register protocol that the implementation follows. Important groups include command/syncpoint/state-control registers, interrupt status/mask/type/polarity bits, display timing registers, output enable bits for HDMI/DSI/SOR/cursor, cursor address/blending registers, window option/color/stride/address registers, legacy blend registers, CSC/filter registers, and Tegra186+ window-group/NVdisplay register aliases.

## State and Persistence
The persistent state described here is split between DRM atomic state (`tegra_dc_state`), device lifetime state (`tegra_dc`), and hardware state represented by register offsets and bit definitions. The register map documents double/triple-buffered programming via `DC_CMD_STATE_CONTROL` update and activate bits, and it exposes both legacy DC window registers and later NVdisplay window-group registers.

## Dependencies and Integration Points
`dc.h` includes Linux host1x and DRM CRTC headers and includes local `drm.h`. It is consumed by display controller implementation, RGB, DSI, SOR/HDMI paths, and code that needs to call `tegra_dc_state_setup_clock()` or `tegra_dc_commit()`. Register definitions integrate with tracepoints through the inline accessors.

## Risks
The header contains many raw register constants with overlapping aliases between legacy and Tegra186+ programming models. Incorrect use of a legacy offset against an NVdisplay window group, or vice versa, can silently program the wrong register. Some bitfield masks include comments noting wider fields on Tegra186, so callers must account for `tegra->hmask`/`vmask` and SoC limits. Because this file is the canonical register vocabulary, stale or incorrect constants have broad blast radius across modesetting, plane updates, interrupts, and output enable paths.

## Test Signals
Build coverage should catch missing prototypes and type drift. Runtime validation comes from successful modesets on each supported SoC generation, trace logs showing expected register offsets, debugfs register dumps matching hardware documentation, correct interrupt status handling, and format/modifier tests that exercise the window color-depth and tiling constants.
