## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ccorr.c

### Purpose

`mtk_disp_ccorr.c` implements the MediaTek DISP_CCORR color-correction block, providing clock control, size/config programming, start/stop, DRM CTM programming, and component registration.

### Important APIs, types, and functions

`struct mtk_disp_ccorr` stores clock, MMIO, CMDQ register metadata, and match data containing matrix precision bits. Public functions are `mtk_ccorr_clk_enable()`, `mtk_ccorr_clk_disable()`, `mtk_ccorr_config()`, `mtk_ccorr_start()`, `mtk_ccorr_stop()`, and `mtk_ccorr_ctm_set()`.

### Control flow

Probe allocates state, gets clock/MMIO, optionally obtains CMDQ metadata, loads SoC match data, and registers as a component. Config writes size and enables the CCORR engine through DDP write helpers. CTM setup exits without a blob, converts the 3x3 DRM S31.32 matrix into signed fixed-point coefficients using SoC-specific precision, and writes five packed coefficient registers. Start/stop toggle the enable register.

### State and persistence behavior

Hardware state includes size, config engine enable, coefficient registers, and enable bit. Software state persists matrix precision and command-queue metadata.

### Dependencies

It depends on DRM color management helpers, component/OF/platform support, clocks, CMDQ, and MediaTek DDP write helpers.

### Integration points

The DDP registry’s `ddp_ccorr` table exposes config/start/stop/CTM callbacks to `mtk_crtc.c`, which calls CTM updates during atomic flush when color management changes.

### Risks

Coefficient precision differs by SoC, so wrong match data changes color transforms. CTM writes use a NULL CMDQ packet and therefore direct MMIO in this implementation. Missing CTM blobs leave previous hardware coefficients untouched.

### Test signals

Signals include CTM DRM property tests, coefficient readback, color transform visual validation, component clock balance, and modesets on MT8183/MT8192 CCORR paths.
