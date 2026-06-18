# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_drv.c

## Purpose
`lcdif_drv.c` is the platform-driver and DRM-device setup for the i.MX LCDIFv3 controller (`imx-lcdif`). It allocates the DRM device, maps registers, obtains clocks, initializes KMS objects, attaches output bridges, installs IRQ handling, and wires runtime/system PM.

## Important APIs, Types, And Functions
Important entry points are `lcdif_probe`, `lcdif_remove`, `lcdif_shutdown`, `lcdif_load`, `lcdif_unload`, `lcdif_irq_handler`, runtime PM callbacks, and system suspend/resume callbacks. The file defines `lcdif_driver` with GEM DMA and fbdev DMA ops, `lcdif_mode_config_funcs`, `lcdif_mode_config_helpers` using `drm_atomic_helper_commit_tail_rpm`, and a simple encoder destroy callback. Device-tree matches are `fsl,imx8mp-lcdif` and `fsl,imx93-lcdif`.

## Control Flow, State, And Integration
Probe allocates `drm_device`, calls `lcdif_load`, registers DRM, then starts DRM client setup. `lcdif_load` allocates `struct lcdif_drm_private`, maps MMIO, gets `pix`, `axi`, and `disp_axi` clocks, sets a 36-bit coherent DMA mask, initializes mode config, calls `lcdif_kms_init`, initializes vblank, attaches one encoder/bridge per OF endpoint, configures dimensions and helper callbacks, requests IRQ, starts polling, and enables runtime PM. The IRQ reads `LCDC_V8_INT_STATUS_D0`, handles vblank only when `VS_BLANK` is set and `SHADOW_LOAD_EN` is clear, then acknowledges status.

## State, Dependencies, And Risks
State lives in `drm->dev_private`: MMIO base, clocks, IRQ, DRM objects, and primary plane/CRTC. Runtime PM owns the clock-enable order: AXI, display AXI, pixel clock on resume and reverse on suspend. Risks include bridge endpoint parsing failures, missed vblank when shadow load is pending, unchecked `clk_prepare_enable()` errors in runtime resume, and PM imbalance if load/unload error paths change. Test signals include DT probe, bridge attach, atomic modeset, vblank wait/page flip behavior, suspend/resume, and interrupt storm absence.
