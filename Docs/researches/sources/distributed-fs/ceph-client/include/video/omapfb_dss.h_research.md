# sources/distributed-fs/ceph-client/include/video/omapfb_dss.h

## Purpose
`omapfb_dss.h` defines the legacy OMAP Display Subsystem fbdev-facing API: display types, planes, overlay managers, timings, DSI configuration, output-driver operation tables, display-device state, driver callbacks, registration APIs, ISR APIs, and CONFIG-dependent stubs.

## Important APIs, Types, and Functions
Important definitions include DISPC IRQ masks, `enum omap_display_type`, `omap_plane`, `omap_channel`, `omap_color_mode`, load modes, transparency key types, signal levels/edges, VENC type, DSI pixel format/mode/transfer mode, display caps/state, rotation type/angle, overlay caps, and output IDs. Core structs include DSI video/config data, `omap_video_timings`, CPR coefficients, `omap_overlay_info`, `omap_overlay`, `omap_overlay_manager_info`, `omap_overlay_manager`, `omap_dsi_pin_config`, `omap_dss_writeback_info`, per-output ops tables for DPI/SDI/DVI/ATV/HDMI/DSI, `omap_dss_device`, and `omap_dss_driver`. APIs under `CONFIG_FB_OMAP2` cover version/init checks, driver/display/output registration, device iteration/find/get/put, timing conversion, feature queries, overlay/manager access, output connection, default helpers, DISPC ISR registration, compatibility init, and OF source lookup; stubs provide compile-time no-op or failure behavior when disabled.

## Control Flow
Display drivers register `omap_dss_driver` callbacks and `omap_dss_device` instances. Outputs connect source and destination devices, managers bind overlays to outputs, overlay info is programmed, managers apply pending state and wait for go/vsync, and DISPC ISRs report frame/underflow/sync events. DSI paths additionally configure pins, bus timing, virtual channels, HS/LP behavior, packet reads/writes, TE, and update callbacks.

## State and Persistence Behavior
Runtime state is rich: display devices track source/destination links, state, manager/output bindings, timing, caps, type-specific PHY fields, panel fields, driver pointer, owner, and resume activation flag. Overlays and managers hold dynamic binding and info state. State lasts while registered and is restored through driver suspend/resume, not persisted across reboot.

## Dependencies and Integration Points
The header depends on Linux list/kobject/device/interrupt APIs, OMAP DSS platform data, videomode, HDMI/audio infoframe forward declarations, and device tree. It integrates fbdev OMAP display, panels, encoders, HDMI/DVI/DSI/VENC outputs, DISPC interrupts, overlay composition, writeback, and DT graph discovery.

## Risks and Test Signals
Risks include calling blocking operations from interrupt context despite comments, state drift between overlay/manager/display objects, CONFIG stub behavior hiding missing dependencies, DSI virtual-channel leaks, timing conversion errors, and sync/underflow interrupt mishandling. Test signals include driver/display/output registration lifecycle, overlay manager apply/go/vsync waits, DISPC ISR mask registration, DSI command/video mode transfers, HDMI EDID/infoframe paths, VENC PAL/NTSC timings, suspend/resume activation, and builds with and without `CONFIG_FB_OMAP2`.
