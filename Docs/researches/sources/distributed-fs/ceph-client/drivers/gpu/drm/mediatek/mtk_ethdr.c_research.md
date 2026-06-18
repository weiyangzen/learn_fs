# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ethdr.c

## Purpose
Implements the MediaTek ETHDR display block, including mixer setup, HDR front-end/back-end bypass configuration, layer blending, vblank IRQ callback plumbing, clocks, resets, and component binding for the DRM pipeline.

## Important APIs, types, and functions
- `struct mtk_ethdr` stores seven MMIO subcomponents, 13 bulk clocks, MMSYS device pointer, optional IRQ, reset control, and vblank callback state.
- `mtk_ethdr_config()` initializes HDR blocks in bypass mode and configures mixer ROI, background, datapath, and MMSYS HDR routing.
- `mtk_ethdr_layer_config()` programs per-layer size, offset, alpha/blend mode, and MMSYS mixer input configuration.
- `mtk_ethdr_start()`, `mtk_ethdr_stop()`, `mtk_ethdr_clk_enable()`, and `mtk_ethdr_clk_disable()` are lifecycle hooks.
- `mtk_ethdr_register_vblank_cb()`, `mtk_ethdr_enable_vblank()`, and related helpers connect frame-complete interrupts to the CRTC.

## Control flow
Probe maps all ETHDR sub-block resources by index, optionally captures CMDQ client register bases, acquires named clocks, requests an IRQ if present, obtains reset controls, and adds a component. Bind stores the MMSYS device pointer supplied by the master. Configuration first bypasses VDO/GFX HDR front-ends and VDO back-end, enables function DCM, sets mixer ROI/background/source defaults, enables layer 0, then asks MMSYS to configure HDR half-width routing and mixer channel swap. Per-layer updates either clear the layer size to disable without switching mixer mode or program aligned even width, offset, alpha, premultiplied/non-premultiplied mode, and source enable bit through CMDQ writes.

## State and persistence
Persistent driver state is limited to mapped resources, clocks, callback pointers, and reset control. Per-frame or per-atomic state arrives from `struct mtk_plane_state` and is committed into hardware registers through CMDQ packets. The vblank callback pointer remains valid until explicitly unregistered; hardware interrupt enable state persists in the mixer registers.

## Dependencies and integration points
Depends on MediaTek CMDQ/DDP write helpers, MMSYS mixer/HDR routing helpers, DRM blend constants, component framework, reset controller API, and platform clocks. It is called by MediaTek CRTC/display component code for blend capability discovery, layer configuration, top-level mode configuration, and vblank handling.

## Risks
Layer widths are aligned down to an even number and odd x coordinates use MMSYS even-extend mode, so off-by-one behavior can show as shifted or clipped output. Disabling a layer by zeroing size instead of `MIX_SRC_CON` is intentional hardware workaround territory. Callback registration is unsynchronized with IRQ handling, so callers must manage lifetime carefully. Missing CMDQ base lookup is only debug-logged, which may matter on systems that require command-queue programming.

## Test signals
Signals include frame-complete IRQ delivery, vblank callback behavior, layer enable/disable without screen shift, premultiplied/coverage/pixel-none blend results, odd x positions, four-layer limits, reset behavior on stop, and clock/reset errors during probe or enable.
