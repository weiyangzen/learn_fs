# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_kms.c

## Purpose

`zynqmp_kms.c` provides DRM/KMS integration for ZynqMP DPSUB in DMA mode. It creates VID/GFX planes, a CRTC, a simple encoder/bridge connector chain, GEM DMA dumb buffers, fbdev setup, vblank handling, and atomic plane/CRTC behavior.

## Important APIs, Types, And Functions

Public APIs are `zynqmp_dpsub_drm_init()`, `zynqmp_dpsub_drm_cleanup()`, and `zynqmp_dpsub_drm_handle_vblank()`. Key helpers include plane atomic check/update/disable, `zynqmp_dpsub_create_planes()`, CRTC atomic enable/disable/begin/flush, vblank enable/disable, `zynqmp_dpsub_dumb_create()`, `zynqmp_dpsub_fb_create()`, and `zynqmp_dpsub_kms_init()`.

## Control Flow

DRM init allocates a managed DRM device, attaches a release action for the subsystem, initializes mode config and vblank, creates planes from display layer format lists, creates a CRTC with GFX as primary and VID as overlay, maps possible CRTCs, initializes an encoder, attaches the DP bridge, creates a bridge connector, registers the DRM device, and starts fbdev emulation with RGB888. Atomic CRTC enable sets the pixel clock, enables `vid_clk`, enables the display, and waits three vblanks for timing stability. Plane update reprograms format if needed, submits layer DMA, applies graphics alpha, and enables the layer. CRTC flush arms vblank events.

## State And Persistence Behavior

Persistent DRM state is `struct zynqmp_dpsub_drm` embedded DRM device plus planes, CRTC, and encoder. Hardware state is delegated to `zynqmp_disp` and `zynqmp_dp`. Vblank state is managed by DRM and DP interrupt enable/disable. Dumb buffer and framebuffer creation enforce `dpsub->dma_align`.

## Dependencies And Integration Points

It depends on DRM atomic, bridge connector, GEM DMA, fbdev DMA, vblank, blend, probe helpers, clocks, PM runtime, and local display/DP APIs. It is only initialized when `dpsub->dma_enabled` is true.

## Risks And Test Signals

Risks include no scaling support, graphics plane as primary with video overlay assumptions, explicit primary-plane disable during CRTC disable, clock/PM leaks on enable failure, vblank event handling, and FB pitch alignment rewriting. Test atomic enable/disable, page flips with vblank events, RGB/YUV format changes, alpha property, dumb buffer alignment, bridge connector EDID/mode validation, and cleanup after unplug.
