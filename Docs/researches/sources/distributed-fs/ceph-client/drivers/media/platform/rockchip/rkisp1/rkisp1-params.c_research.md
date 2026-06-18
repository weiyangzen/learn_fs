# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-params.c

## Purpose

`rkisp1-params.c` implements the RKISP1 ISP parameter metadata output video node. Userspace queues fixed (`V4L2_META_FMT_RK_ISP1_PARAMS`) or extensible (`V4L2_META_FMT_RK_ISP1_EXT_PARAMS`) parameter buffers; the driver copies and validates those buffers, applies their module configuration to ISP registers at frame boundaries, and completes buffers with the frame sequence for which the settings take effect. The file is the main bridge between the V4L2 metadata API, videobuf2 queueing, RKISP1 per-frame ISP tuning, and the low-level register map in `rkisp1-regs.h`.

## Important APIs, Types, And Functions

The local `union rkisp1_ext_params_config` overlays all extensible block payloads with a common `rkisp1_ext_params_block_header`. `rkisp1_params_formats` defines the two accepted metadata formats and their buffer sizes. `rkisp1_params_get_format_info()` maps a V4L2 dataformat to a supported format, defaulting to the legacy fixed format.

Hardware programming helpers include `rkisp1_param_set_bits()` and `rkisp1_param_clear_bits()`, plus module-specific functions such as `rkisp1_dpcc_config()`, `rkisp1_bls_config()`, `rkisp1_lsc_config()`, `rkisp1_flt_config()`, `rkisp1_sdg_config()`, `rkisp1_goc_config_v10()`, `rkisp1_goc_config_v12()`, `rkisp1_ctk_config()`, `rkisp1_awb_meas_config_v10/v12()`, `rkisp1_aec_config_v10/v12()`, `rkisp1_hst_config_v10/v12()`, `rkisp1_afm_config_v10/v12()`, `rkisp1_ie_config()`, `rkisp1_csm_config()`, `rkisp1_dpf_config()`, the compand helpers, and `rkisp1_wdr_config()`.

Version-specific behavior is selected through `struct rkisp1_params_ops`, with `rkisp1_v10_params_ops` and `rkisp1_v12_params_ops` providing different LSC table packing, gamma output packing, AWB/AEC/HST register layouts, and AFM shift programming. The V4L2/vb2 surface is provided by `rkisp1_params_ioctl`, `rkisp1_params_fops`, `rkisp1_params_vb2_ops`, `rkisp1_params_register()`, and `rkisp1_params_unregister()`.

## Control Flow

Userspace opens the params video node registered by `rkisp1_params_register()`, negotiates a metadata format, allocates two to eight buffers, fills them with ISP parameters, and queues them through vb2. `rkisp1_params_vb2_buf_init()` allocates an internal scratch buffer sized to the selected metadata format. `rkisp1_params_vb2_buf_prepare()` validates the payload size and copies user memory into that scratch buffer so userspace cannot alter it while the ISR later applies it. Extensible buffers additionally pass through `v4l2_isp_params_validate_buffer_size()` and `v4l2_isp_params_validate_buffer()`.

Queued buffers are appended to `params->params` under `config_lock`. `rkisp1_params_pre_configure()` programs default AWB, AEC, AFM, histogram, color-space matrix, quantization, YCbCr encoding, and Bayer pattern before streaming. If a buffer is already queued, it applies non-LSC parameters immediately. `rkisp1_params_post_configure()` applies LSC after ISP start because some hardware gates LSC RAM behind `ISP_CTRL.ISP_ENABLE`.

During streaming, `rkisp1_params_isr()` is called on frame completion. It takes the first queued buffer, applies all fixed-format groups or all extensible block groups, sets `RKISP1_CIF_ISP_CTRL_ISP_CFG_UPD`, completes the vb2 buffer, and reports `frame_sequence + 1` to describe the frame that will observe the parameters. Fixed-format flow is split across `rkisp1_isp_isr_other_config()`, `rkisp1_isp_isr_lsc_config()`, and `rkisp1_isp_isr_meas_config()`. Extensible flow walks block headers in `rkisp1_ext_params_config()` and dispatches by block type through `rkisp1_ext_params_handlers`.

## State And Persistence

Persistent driver state is in `struct rkisp1_params`: selected `metafmt`, queued params list, `enabled_blocks` bitmask for extensible block state, raw Bayer pattern, quantization, YCbCr encoding, hardware ops, and locks. No state is persisted beyond the device lifetime; state lives in kernel memory and hardware registers. Many config functions deliberately preserve existing enable bits while changing tuning registers, because enable state is controlled separately by module enable updates or extensible block flags. LSC uses hardware double-buffered SRAM selection based on `RKISP1_CIF_ISP_LSC_STATUS`.

`rkisp1_params_disable()` clears all major ISP processing enables when the camera is inactive. `rkisp1_params_vb2_stop_streaming()` completes queued buffers with `VB2_BUF_STATE_ERROR` and resets `enabled_blocks`.

## Dependencies And Integration Points

This file depends on V4L2 core, V4L2 events, the media controller, videobuf2 vmalloc memory, `media/v4l2-isp.h` extensible parameter validation, and internal RKISP1 helpers from `rkisp1-common.h`. It programs register names and bitfields from `rkisp1-regs.h`. It is integrated with the ISP frame ISR, the media graph through one source pad, and userspace 3A/control loops through metadata output buffers. Feature bits such as `RKISP1_FEATURE_BLS` and `RKISP1_FEATURE_COMPAND` gate unsupported extensible blocks.

## Risks

The largest risks are hardware sequencing and bit preservation. Writing a module register without preserving its enable bit can accidentally turn processing on or off; the file repeatedly masks or restores enables to avoid that. LSC is timing-sensitive because table RAM access may require the ISP to be enabled. Extensible parameter walking trusts prior validation for block bounds; validation regressions would make the variable-length loop dangerous. Version-specific packing is easy to break because v10 and v12 share semantic blocks but not always register layout or field width. Buffer completion sequence numbers are also subtle: reporting the wrong sequence would mislead userspace 3A algorithms.

## Test Signals

Useful signals include V4L2 metadata format enumeration and try/set/get coverage for both fixed and extensible formats, buffer queueing with invalid payload sizes, streaming with no queued buffers, streaming with multiple queued buffers, and stop-streaming error completion. Hardware or emulation tests should verify that parameter buffers are completed once, `enabled_blocks` tracks extensible enable/disable flags, unsupported feature blocks are ignored, LSC updates occur after ISP enable, and AWB/AEC/HST/AFM statistics respond to applied measurement windows on both v10 and v12 register layouts.
