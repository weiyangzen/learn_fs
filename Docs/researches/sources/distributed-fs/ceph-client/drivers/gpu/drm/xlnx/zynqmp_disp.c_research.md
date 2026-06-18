# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp.c

## Purpose

`zynqmp_disp.c` drives the display-controller portion of the ZynqMP DP subsystem: AV buffer manager, video blender, audio buffer routing, DRM display layers, DPDMA channel setup, live-input format setup, and display clock programming.

## Important APIs, Types, And Functions

Key types are `struct zynqmp_disp`, `struct zynqmp_disp_layer`, `struct zynqmp_disp_layer_dma`, and `struct zynqmp_disp_format`. Public APIs include `zynqmp_disp_probe()`, `zynqmp_disp_remove()`, `zynqmp_disp_enable()`, `zynqmp_disp_disable()`, `zynqmp_disp_setup_clock()`, `zynqmp_disp_blend_set_global_alpha()`, `zynqmp_disp_layer_drm_formats()`, `zynqmp_disp_live_layer_formats()`, `zynqmp_disp_layer_set_format()`, `zynqmp_disp_layer_set_live_format()`, `zynqmp_disp_layer_update()`, `zynqmp_disp_layer_enable()`, and `zynqmp_disp_layer_disable()`.

## Control Flow

Probe maps `blend` and `av_buf` resources, creates VID/GFX layers, chooses non-live DPDMA mode or live mode from `dpsub->dma_enabled`, requests DPDMA channels in non-live mode, and exports layer pointers to `dpsub`. Format setup writes AV buffer format fields and component scaling factors. Plane updates prepare repeating interleaved DMA descriptors per framebuffer plane and start DPDMA channels. Enabling the display configures RGB blender output, background, clock sources, AV buffer reset, channel burst lengths, and audio routing. Layer enable/disable coordinates AV buffer output selection and blender CSC/layer control.

## State And Persistence Behavior

Persistent software state includes mapped register bases, layer format/mode pointers, DMA channels, current DRM format, and DPDMA alignment exported through `dpsub->dma_align`. Hardware state persists in AV buffer format/output/channel/reset/clock registers, blender output/CSC/background/global-alpha/layer-control registers, and running DPDMA descriptors until terminated.

## Dependencies And Integration Points

It depends on DRM format/framebuffer/plane helpers, `drm_fb_dma_get_gem_addr()`, DMAengine interleaved transfers, Xilinx DPDMA peripheral config, media bus formats, common clocks through `dpsub`, and register definitions from `zynqmp_disp_regs.h`. It integrates with `zynqmp_kms.c` for non-live planes and `zynqmp_dp.c` for live input bus formats.

## Risks And Test Signals

Risks include unsupported hybrid live/non-live mode, strict no-scaling assumptions, DMA descriptor/pitch alignment errors, incorrect RGB/YUV swap or CSC matrix programming, channel termination races, and clock source mismatch between DT and hardware. Test VID/GFX formats including multi-plane YUV, alpha on graphics layer, live input bus-format negotiation, DMA alignment in dumb buffers and FB pitches, enable/disable cycles, and underflow/overflow interrupt diagnostics from DP.
