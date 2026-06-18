# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_ade_reg.h

Purpose: defines the Kirin ADE display controller register map, bitfields, hardware enums, and update helper used by the ADE CRTC/plane implementation.

Important APIs/types: macros cover ADE control/reload/reset, RDMA channel registers, overlay routing/control/output size, color transform, clip, LDI timing/control/interrupts, DSI pixel clock gate, and media NoC QoS registers. Enums describe frame-effect timing, framebuffer formats, channels, scaler/ctran/overlay IDs, alpha modes, LDI output/work/input modes, DSI pixel clock gate values, and QoS modes.

Control flow: no runtime flow. `kirin_drm_ade.c` uses these definitions for power-up initialization, LDI mode programming, RDMA/clip/compositor setup, vblank IRQ handling, and QoS configuration.

State and persistence: hardware state is stored in ADE registers. Reload-disable bits govern when changes take effect in hardware.

Dependencies and integration points: relies on Linux `readl/writel`, `BIT_ULL`, and bit macros. It is tightly coupled to ADE channel count and the primary-plane-only setup.

Risks: `ADE_CH_NUM` is currently one, so many helper macros imply broader hardware but driver data exposes only primary plane. `MASK(32)` uses 64-bit math to avoid overflow, but callers must still use sensible widths. Offsets and reload bits are critical for frame-synchronized updates.

Test signals: ADE register dumps, vblank interrupt behavior, primary plane RDMA scanout, clipping, overlay routing, LDI timing, and QoS register writes.
