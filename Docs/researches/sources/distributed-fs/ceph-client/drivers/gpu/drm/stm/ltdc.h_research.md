# sources/distributed-fs/ceph-client/drivers/gpu/drm/stm/ltdc.h

## Purpose
`ltdc.h` defines the shared STM LTDC device model and public functions used by `drv.c` and `ltdc.c`. It captures hardware capability flags, runtime counters, platform data, and the LTDC device state stored in `drm_device->dev_private`.

## Important APIs, Types, and Functions
- `struct ltdc_caps`: per-hardware-version capability map including layer count, register layout, bus width, supported pixel formats, pad frequency, IRQ count, YCbCr, shadow registers, CRC, z-order, rotation, and FIFO threshold support.
- `struct fps_info`: per-plane update counter and timestamp for debug state output.
- `struct ltdc_plat_data`: OF match data carrying pad maximum frequency.
- `struct ltdc_device`: MMIO/regmap/clocks, error lock/counters, capability data, suspend state, CRC state, and per-plane FPS state.
- `ltdc_load`, `ltdc_unload`, `ltdc_suspend`, `ltdc_resume`: core LTDC lifecycle API.

## Control Flow, State, and Persistence
The header has no direct control flow, but its structures define the persistent state initialized in `drv_load` and populated in `ltdc_load`. `suspend_state` persists an atomic modeset snapshot across system suspend. Error counters persist until printed, reset, or CRTC disable clears them.

## Dependencies and Integration Points
It is included by the STM platform driver and LTDC implementation. It relies on DRM, regmap, clocks, mutexes, and atomic-state types being available to including files.

## Risks and Test Signals
Risks include feature flags becoming inconsistent with hardware tables, exposed mutable state in `ltdc_device`, and fixed `LTDC_MAX_LAYER` assumptions. Tests should compile all STM driver combinations and exercise capability-dependent paths for CRC, YCbCr, dynamic z-order, rotation, FIFO threshold, and multiple hardware versions.
