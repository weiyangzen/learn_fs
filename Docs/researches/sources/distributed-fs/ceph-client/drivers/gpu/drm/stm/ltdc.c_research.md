# sources/distributed-fs/ceph-client/drivers/gpu/drm/stm/ltdc.c

## Purpose
`ltdc.c` implements the STM LTDC DRM/KMS hardware driver. It detects LTDC capabilities by hardware version, creates the CRTC, planes, and encoder bridge chain, programs display timings and layer registers, handles vblank/error/CRC interrupts, and manages clocks, reset, runtime PM, YCbCr conversion, z-order, rotation, and shadow-register commits.

## Important APIs, Types, and Functions
- Capability tables map hardware versions to layer register layouts, DRM formats, native pixel formats, IRQ count, bus width, CRC, YCbCr, rotation, dynamic z-order, and FIFO-threshold support.
- `ltdc_load`/`ltdc_unload`, `ltdc_suspend`/`ltdc_resume`: public entry points used by `drv.c`.
- CRTC helpers: mode validation/fixup, timing programming, vblank/CRC control, scanout-position reporting, atomic enable/disable/flush.
- Plane helpers: `ltdc_plane_atomic_check`, `ltdc_plane_atomic_update`, disable/print-state, and `ltdc_plane_create`.
- Encoder helpers enable/disable LTDC output and bridge attach.
- IRQ handlers count transfer/FIFO errors, handle vblank, and optionally publish CRC entries.

## Control Flow, State, and Persistence
`ltdc_load` acquires clocks, discovers endpoint bridges/panels, resets hardware, maps registers through regmap, reads capabilities, clears interrupts, requests all IRQs, creates CRTC/planes, initializes vblank, disables clocks, selects sleep pinctrl, and enables runtime PM. Atomic modesetting sets pixel clock, bridge/connector bus flags, timing registers, output YCbCr conversion, line IRQ position, and shadow reload policy. Plane updates compute window positions from back porch, translate formats, write DMA addresses and pitches, configure alpha/blending/z-order, optional YCbCr auxiliary planes and coefficients, rotation mirroring, CLUT, and layer enable bits.

Persistent state is in `struct ltdc_device`: registers, clocks, capability flags, IRQ/error counters under `err_lock`, FIFO threshold, per-plane FPS counters, suspend state, and CRC state.

## Dependencies and Integration Points
The file depends on DRM atomic, bridge/panel, GEM DMA framebuffer helpers, vblank/CRC, regmap MMIO, common clock, reset, pinctrl PM, OF graph, and `ltdc.h`. It is called by the STM DRM platform driver and connects LTDC output to panels, DSI, LVDS, or other bridges.

## Risks and Test Signals
Risks include complex hardware-version tables, 32-bit DMA address truncation, unsupported scaling, subtle negative pitch/reflection math, YCbCr plane address calculations, PM clock ordering, precise clock filtering, and IRQ counter races. Tests should cover every supported hardware version, all advertised formats and modifiers, alpha/z-order/rotation properties, CRC source enable/disable, FIFO underrun reporting, bridge bus flags, suspend/resume with active scanout, and KMS atomic tests for invalid scaling and unsupported modes.
