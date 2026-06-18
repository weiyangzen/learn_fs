# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-scaler.c

## Purpose
Programs the three-channel DCSS scaler block. It designs fixed-point Gaussian or nearest-neighbor filter coefficients, handles RGB/YUV format and chroma geometry, computes scaling increments, writes scaler coefficients through the context loader, and defers scaler control writes for interrupt-safe commit.

## Important APIs, types, and functions
- `struct dcss_scaler` owns the context-loader link and three `struct dcss_scaler_ch` channels.
- Public APIs are `dcss_scaler_init()`, `dcss_scaler_exit()`, `dcss_scaler_ch_enable()`, `dcss_scaler_get_min_max_ratios()`, `dcss_scaler_set_filter()`, `dcss_scaler_setup()`, and `dcss_scaler_write_sclctrl()`.
- Fixed-point/filter helpers include `mult_q()`, `div_q()`, `exp_approx_q()`, `dcss_scaler_gaussian_filter()`, `dcss_scaler_nearest_neighbor_filter()`, and `dcss_scaler_filter_design()`.
- Programming helpers include `dcss_scaler_format_set()`, `dcss_scaler_res_set()`, `dcss_scaler_fractions_set()`, `dcss_scaler_program_5_coef_set()`, `dcss_scaler_program_7_coef_set()`, `dcss_scaler_yuv_coef_set()`, `dcss_scaler_rgb_coef_set()`, `dcss_scaler_bit_depth_set()`, and `dcss_scaler_set_rgb10_order()`.

## Control flow
Initialization allocates the scaler object, maps three channel register windows at 0x400 spacing, and sets the context-loader context to `CTX_SB_HP`. Plane updates first select nearest-neighbor versus default filtering, then call `dcss_scaler_setup()` with source/destination sizes and format. Setup classifies the source as RGB, YUV420, YUV422, or 4:4:4-like RGB/YUV output, enables YUV and 8-line RTRAM when needed, computes luma/chroma fractions and chroma phase starts, designs and writes coefficients for luma and chroma, programs bit depth, 10-bit RGB component ordering, source/destination format, and luma/chroma resolutions.

Channel enable only updates cached `sdata_ctrl` and `scaler_ctrl` state and marks `scaler_ctrl_chgd` when the control word changed. `dcss_scaler_write_sclctrl()` is the interrupt-context path: it asserts the context-loader lock and writes changed `SCALER_CTRL` values with `dcss_ctxld_write_irqsafe()`.

## State and persistence
Each channel persists cached scaler data-control bits, scaler-control bits, changed flag, chroma start phases, and filter mode. Filter coefficients and geometry are queued into the DCSS context loader and take effect with the broader DCSS context switch. `dcss_scaler_exit()` directly clears hardware control registers for all channels.

## Dependencies and integration points
Depends on DCSS context-loader APIs, DRM format metadata, and Linux fixed-width math helpers including `div_s64()`. It is called by DCSS plane atomic updates for every full plane setup and by the CRTC/context-load path for interrupt-safe scaler-control commit.

## Risks
The coefficient generator uses custom fixed-point math and approximated exponentials; overflow, divide-by-zero, or normalization mistakes can produce bad filters. Several resolution writes subtract one from source/destination dimensions, so atomic checks must keep dimensions nonzero. Chroma-location constants are fixed to one location in setup, which may not match all content. The scaler-control write is intentionally delayed; missing `dcss_scaler_write_sclctrl()` calls can leave channel enable state stale. `vrefresh_hz` is accepted but unused, so timing-dependent scaler choices cannot currently vary with refresh rate.

## Test signals
Useful tests cover RGB565/8888/10-bit RGB formats, NV12/NV21 YUV420, packed YUV422, equal-size identity filtering, downscale/upscale extremes per channel, nearest-neighbor property selection, enable/disable transitions, interrupt-context scaler control writes, and visual checks for chroma alignment and 10-bit component order.
