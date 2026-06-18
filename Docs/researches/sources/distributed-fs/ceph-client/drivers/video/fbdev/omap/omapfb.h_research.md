# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/omapfb.h

## Purpose
`omapfb.h` is the private interface for the legacy OMAP1 framebuffer driver. It defines panel, external interface, controller, memory, plane, notifier, and device structures used across `omapfb_main.c`, `lcdc.c`, HWA742, SoSSI, and panel drivers.

## Important APIs, Types, And Functions
- `struct lcd_panel` describes board/panel timing, format, lifecycle hooks, backlight hooks, capability hooks, and diagnostics.
- `struct lcd_ctrl_extif` abstracts an external bus for register/data transfers, timing conversion, transfer-area DMA, and tear-sync.
- `struct lcd_ctrl` abstracts a display controller backend with init/cleanup, caps, update mode, plane/memory setup, mmap, scale/rotation, update window, sync, PM, test, palette, and color-key methods.
- `struct omapfb_device` ties together panel, controller, extif, IRQs, state, memory descriptor, fb_info array, palette, and a dummy DSS clock device.
- Notifier APIs allow clients to register for READY/DISABLED events.

## Control Flow
The header establishes function-pointer contracts. Runtime flow is provided by implementations that fill `struct lcd_ctrl`, `struct lcd_ctrl_extif`, and `struct lcd_panel`.

## State And Persistence
No concrete state is allocated here, but the structures define all major runtime state boundaries for the OMAP1 fbdev stack. State is process-local kernel memory and not persistent.

## Dependencies And Integration Points
It depends on kernel fbdev types, mutexes, and public OMAP fbdev UAPI types in `linux/omapfb.h`. It is the integration contract between board panel drivers, internal/external controller drivers, and `omapfb_main.c`.

## Risks
The single-plane assumption is encoded as `OMAPFB_PLANE_NUM 1`. Several callbacks are optional, so callers must guard null pointers. The function-pointer API predates modern DRM/component conventions and relies heavily on platform data and global registration order.

## Test Signals
Build success across all legacy OMAP fbdev files, correct panel/controller registration, and notifier/client behavior validate this private API.
