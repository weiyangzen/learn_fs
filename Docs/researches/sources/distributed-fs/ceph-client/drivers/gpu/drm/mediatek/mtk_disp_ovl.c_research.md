## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ovl.c

### Purpose

`mtk_disp_ovl.c` implements the classic MediaTek DISP_OVL overlay engine. It exposes plane-layer count, supported formats, blending capabilities, AFBC support, vblank IRQ handling, clock control, ROI setup, layer enable/disable, format conversion, rotation/reflection handling, and platform-specific OVL data.

### Important APIs, types, and functions

`struct mtk_disp_ovl_data` describes register address layout, GMC bit width, layer count, RGB565/RGB888 encoding variant, SMI ID behavior, AFBC support, DRM blend modes, formats, and extended color-format support. `struct mtk_disp_ovl` stores CRTC/vblank callback state, clock, MMIO, CMDQ register, and data.

Important exported hooks include `mtk_ovl_register_vblank_cb()`, `mtk_ovl_enable_vblank()`, `mtk_ovl_get_blend_modes()`, `mtk_ovl_get_formats()`, `mtk_ovl_is_afbc_supported()`, `mtk_ovl_clk_enable()`, `mtk_ovl_start()`, `mtk_ovl_config()`, `mtk_ovl_layer_nr()`, `mtk_ovl_layer_check()`, `mtk_ovl_layer_config()`, and `mtk_ovl_bgclr_in_on/off()`.

### Control flow

Probe obtains IRQ, clock, MMIO, optional CMDQ register, platform data, registers the IRQ handler, enables runtime PM, and adds the component. The IRQ handler clears frame-completion status and calls the registered vblank callback.

CRTC configuration writes ROI size, opaque black background color, and pulses reset. Start enables SMI ID if required and sets `DISP_REG_OVL_EN`; stop clears enable and SMI ID. Plane validation rejects unsupported rotations and rotated/reflected YUV layers. `mtk_ovl_layer_config()` exits through `mtk_ovl_layer_off()` when disabled; otherwise it converts DRM format and blend mode to OVL control bits, applies constant alpha, handles pixel-alpha ignore rules, turns 180-degree rotation into X/Y reflection, adjusts base addresses for reflection, toggles AFBC, writes control/pitch/size/offset/address/header registers, updates extended bit depth, and enables layer RDMA plus source bit.

### State and persistence behavior

Software state includes vblank callback pointers and immutable platform data. Hardware state persists in OVL registers: enabled state, ROI, background color, source layer enables, per-layer format/control/address/pitch/size/offset, AFBC header address/pitch, RDMA GMC thresholds, extended color depth, and datapath options. Layer programming is CMDQ-capable, so atomic updates can be synchronized with display events.

### Dependencies

The driver uses DRM format/blend/framebuffer metadata, Linux clock/component/PM/IRQ/platform/CMDQ APIs, and local MediaTek DDP, CRTC, display, and DRM headers. It depends on `mtk_plane_state` pending fields prepared by the DRM plane path and on `mtk_ddp_write*()` helpers.

### Integration points

OVL is a primary CRTC input component in many path arrays in `mtk_drm_drv.c`. Its DMA device can be used for GEM allocation through CRTC helpers. Plane initialization queries its format and blend support. Vblank is reported through the callback registered by the CRTC. AFBC and 10-bit support affect modifier and format exposure on MT8195.

### Risks

Format conversion has SoC-specific RGB565/RGB888 encodings and blend-mode-dependent premultiplied formats; adding formats without matching hardware encodings can silently corrupt pixels. Reflection adjusts addresses using pitch and height but assumes pending state has already been clipped and validated. AFBC enables are keyed only on non-linear modifier and require correct header address and pitch. The IRQ handler returns `IRQ_NONE` when no callback is registered after clearing status, which is acceptable but can look like a spurious interrupt. GMC threshold programming depends on `gmc_bits` and differs for 8-bit versus 10-bit hardware.

### Test signals

Signals include KMS plane tests across all advertised formats, alpha and premultiplied blend modes, X/Y reflection and 180-degree rotation, YUV non-rotated layers, AFBC and linear modifiers, 10-bit RGB on MT8195, vblank events, suspend/resume, and register traces for source enables and RDMA GMC setup.
