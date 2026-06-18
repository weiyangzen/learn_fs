# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_ade.c

Purpose: implements the Kirin Hi6220 ADE CRTC and plane backend. It allocates ADE hardware context, controls clocks/reset/power, handles vblank, programs LDI timing, RDMA, clipping, compositor routing, and exposes ADE-specific `kirin_drm_data` to the master driver.

Important APIs/functions: `ade_hw_ctx_alloc()` maps registers, gets reset, NoC regmap, IRQ, and clocks, and requests the vblank IRQ. CRTC helpers include mode fixup, mode set, atomic begin/flush/enable/disable, and vblank enable/disable. Plane helpers validate no scaling and bounds, update RDMA/clip/compositor, and disable channels. `ade_driver_data` exports format lists, DRM funcs, config limits, and context callbacks.

Control flow: master private init calls `alloc_hw_ctx()`, creates planes and CRTC using data from `ade_driver_data`. Atomic mode setting powers up if needed, rounds and sets pixel clock, writes LDI timing, enables ADE/LDI and overlay, and arms vblank events. Plane updates write DMA address from GEM DMA object, source clipping, and overlay routing. Disable powers down core clock/reset/media NoC.

State and persistence: `struct ade_hw_ctx` stores MMIO base, clocks, reset, NoC regmap, power flag, IRQ, and CRTC pointer. `struct kirin_crtc` stores enable flag. Hardware registers persist while powered; context is devm-managed.

Dependencies and integration points: depends on DRM atomic/GEM DMA helpers, clk/reset/regmap/syscon/platform APIs, vblank core, and `kirin_ade_reg.h`. Integrates with Kirin master through `ade_driver_data` and with DSI through LDI/DSI pixel gate.

Risks: only one channel/primary plane is exposed despite broader ADE hardware. `ade_power_up()` does not unwind earlier clock/reset enables if a later step fails. `ade_crtc_enable_vblank()` ignores a failed power-up cast to void. No scaling is supported. Debug register dump path is compiled on by `ADE_DEBUG 1`.

Test signals: platform resource acquisition, IRQ delivery, pixel clock rounding, primary plane scanout, no-scaling rejection, vblank event delivery, enable/disable power transitions, DMA address correctness, and DSI panel output.
