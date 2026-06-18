<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sh_mobile_lcdc.h -->
# sources/distributed-fs/ceph-client/include/video/sh_mobile_lcdc.h

## Purpose
This header defines Renesas SH Mobile LCDC register bits and platform data structures for LCD channels, system-bus panels, backlight, transmitters, and overlays.

## Important APIs, Types, And Functions
- `_LDDCKR`, `_LDINTR`, `_LDSR`, `_LDCNT*`, `_LDRCNTR`, and `_LDDDSR` constants cover clock source, interrupts/status, controller enable/reset, and bus/data status.
- `LDMT1R_*`, `LDDFR_*`, `LDSM*`, and `LDPMR_*` encode interface type, polarity, dot-clock controls, input format, and pixel format.
- Interface enums map to RGB, YUV, and system-bus modes such as `RGB16`, `RGB24`, `SYS8A`, and `SYS16A`.
- `struct sh_mobile_lcdc_sys_bus_ops` provides index/data/read callbacks for system-bus panels.
- `struct sh_mobile_lcdc_panel_cfg`, `sh_mobile_lcdc_bl_info`, `sh_mobile_lcdc_overlay_cfg`, `sh_mobile_lcdc_chan_cfg`, and `sh_mobile_lcdc_info` describe panel dimensions, lifecycle hooks, backlight, overlays, channels, modes, transmitter devices, and global clock source.

## Control Flow
Probe consumes `sh_mobile_lcdc_info`, configures per-channel clock/interface flags, registers modes, optionally sets up system-bus operations, powers the panel, starts transfers, and programs overlays. Runtime flow toggles display/backlight hooks, handles LCDC interrupts, and updates channel framebuffers and transmitter devices.

## State And Persistence
State is split between LCDC registers, platform descriptors, framebuffer modes, overlay limits, panel callbacks, and optional backlight state. System-bus deferred I/O delay is a persistent policy in `sys_bus_cfg`.

## Dependencies And Integration Points
It depends on fbdev video modes and Linux platform devices. Integration points include panel code, HDMI/DSI transmitter devices, sys-bus panel command/data paths, backlight callbacks, clock trees, and overlay FourCC negotiation.

## Risks And Edge Cases
Polarity flags are panel-sensitive; incorrect values can blank or destabilize panels. System-bus callbacks can be NULL or slow and must match `interface_type`. Overlay maximum resolution and FourCC values must match hardware capabilities.

## Test Signals
Expected tests cover RGB and system-bus panels, display on/off callbacks, backlight brightness control, correct interrupt/status handling, supported FourCC overlays, external transmitter attachment, and suspend/resume register restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sh_mobile_lcdc.h -->
