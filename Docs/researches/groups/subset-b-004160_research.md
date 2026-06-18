# subset-b-004160 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-params.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-regs.h

## Purpose

`rkisp1-regs.h` is the register and bitfield contract for the RKISP1 driver. It defines ISP control bits, interrupt masks, memory-interface format fields, resizer and dual-crop control bits, MIPI/SMIA status fields, ISP statistics layout, image-processing block masks, and the absolute register offsets used by the C source files. It contains no executable code, but every register read/write in the RKISP1 driver depends on these definitions being accurate for the supported ISP variants.

## Important APIs, Types, And Macros

The header exports macros only. The first half defines field values and masks, including `RKISP1_CIF_ISP_CTRL_*`, acquisition property values, `RKISP1_CIF_ISP_*` interrupt bits, MI control format bits and masks, `RKISP1_CIF_RSZ_CTRL_*`, clock/reset bits, dual-crop modes, MIPI error masks, histogram packing helpers, AWB/AEC extraction and packing helpers, LSC table packing helpers, DPCC masks, BLS modes, AFM window packing, DPF flags, compand control bits, and WDR masks.

The second half defines the address map. Major bases include control (`0x00000000`), image effects (`0x00000200`), ISP core (`0x00000400`), color processing (`0x00000800`), dual crop (`0x00000880`), main/self resizers (`0x00000c00` and `0x00001000`), memory interface (`0x00001400`), SMIA (`0x00001a00`), MIPI (`0x00001c00`), AFM (`0x00002000`), LSC (`0x00002200`), image stabilization (`0x00002300`), v10 histogram (`0x00002400`), filter/CAC/AEC/BLS/DPF/DPCC/WDR (`0x00002500` through `0x00002a00`), v12 histogram (`0x00002c00`), VSM (`0x00002f00`), compand (`0x00003200`), and CSI0 (`0x00007000`).

## Control Flow

There is no runtime control flow in the header. Its definitions are consumed by control flow in the params, stats, resizer, capture, ISP, and CSI/MIPI portions of the driver. A common pattern is: a C file computes a register value with these masks, writes it with `rkisp1_write()`, and triggers a shadow update bit such as `RKISP1_CIF_ISP_CTRL_ISP_CFG_UPD`, `RKISP1_CIF_RSZ_CTRL_CFG_UPD`, or `RKISP1_CIF_DUAL_CROP_CFG_UPD`.

The header encodes variant-specific control flow indirectly. v10 and v12 use different histogram and AEC layouts, different LSC table element widths, different gamma output packing, and different AWB register aliases. Source files select the right macro families by checking the ISP version and dispatching through ops tables.

## State And Persistence

The header itself has no state. It describes persistent hardware register state: enable bits, shadow registers, interrupt status/clear registers, DMA address registers, format registers, measurement accumulators, and table memories. Several definitions refer to shadow registers (`*_SHD`) or update bits, reflecting that hardware state is double-buffered and only applied at defined synchronization points.

## Dependencies And Integration Points

The macros rely on kernel bit helpers such as `BIT()` and `GENMASK()` being available through includers. Integration is broad: `rkisp1-params.c` uses ISP processing block registers, `rkisp1-stats.c` reads measurement output registers, `rkisp1-resizer.c` uses RSZ and dual-crop offsets, capture code uses MI registers, and ISP/MIPI code uses interrupt and input-format definitions. Because this header is included through `rkisp1-common.h`, changes can affect most of the RKISP1 driver.

## Risks

The main risk is silent hardware misprogramming. Wrong masks, shifts, or offsets compile cleanly but can corrupt image data, break DMA, lose interrupts, or report invalid statistics. Overlapping v10/v12 aliases are especially sensitive because the same numeric offsets can mean different layouts. Macros that pack multiple samples per register must match the hardware bit width exactly. Register update bits are also easy to misuse; failing to assert the correct synchronous or asynchronous update bit can leave software state diverged from active hardware state.

## Test Signals

Good signals include compile coverage across RKISP1 users, sparse/build warnings for macro use, camera streaming smoke tests, media graph format negotiation, frame capture validation for raw and YUV formats, v10/v12 statistics sanity checks, interrupt error-counter monitoring, and register traces around params/resizer reconfiguration. Hardware bring-up should compare written offsets and bitfields against the datasheet for each supported ISP revision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-resizer.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-resizer.c

## Purpose

`rkisp1-resizer.c` implements the RKISP1 mainpath and selfpath V4L2 subdevices that crop and scale frames between the ISP source and capture devices. It exposes pad format and crop controls, constrains formats according to path capabilities, programs the dual-crop block when available, and configures the hardware resizer for luma/chroma scaling or YUV subsampling conversion.

## Important APIs, Types, And Functions

`struct rkisp1_rsz_yuv_mbus_info` maps supported YUV media-bus codes to horizontal and vertical chroma divisors. `struct rkisp1_rsz_config` stores path-specific dimensions and dual-crop register offsets. `rkisp1_rsz_config_mp` and `rkisp1_rsz_config_sp` describe mainpath and selfpath limits.

Low-level helpers are `rkisp1_rsz_read()`, `rkisp1_rsz_write()`, `rkisp1_rsz_update_shadow()`, `rkisp1_rsz_calc_ratio()`, `rkisp1_dcrop_disable()`, `rkisp1_dcrop_config()`, `rkisp1_rsz_disable()`, `rkisp1_rsz_config_regs()`, and `rkisp1_rsz_config()`. V4L2 pad operations include `rkisp1_rsz_enum_mbus_code()`, `rkisp1_rsz_init_state()`, `rkisp1_rsz_set_fmt()`, `rkisp1_rsz_get_selection()`, and `rkisp1_rsz_set_selection()`. Streaming and registration are handled by `rkisp1_rsz_s_stream()`, `rkisp1_rsz_register()`, `rkisp1_resizer_devs_register()`, and `rkisp1_resizer_devs_unregister()`.

## Control Flow

Registration creates one resizer subdevice per active RKISP1 path. Mainpath uses `RKISP1_CIF_MRSZ_BASE`; selfpath uses `RKISP1_CIF_SRSZ_BASE`. Each subdevice has a mandatory sink pad and source pad. Initial state sets both pads to `MEDIA_BUS_FMT_YUYV8_2X8`, default width/height, SRGB colorimetry, limited range YUV, and a full-frame sink crop.

During format negotiation, sink format changes validate the requested media-bus code against ISP-source formats, force selfpath to YUYV8_2X8, clamp dimensions, set appropriate colorimetry and quantization, propagate color fields to the source pad, and refresh the sink crop. Source format changes let YUV streams choose supported YUV output bus codes and clamp output size to path-specific resizer limits.

Crop selection is sink-only. `rkisp1_rsz_set_sink_crop()` disables cropping for mainpath Bayer raw data and for hardware without dual crop. Otherwise it aligns left and width to even values and adjusts the rectangle to fit the sink format.

On stream start, `rkisp1_rsz_s_stream()` locks the active subdev state, configures resizer ratios, and configures dual crop if present. If another path is already streaming on selfpath-capable hardware, it requests asynchronous shadow updates; otherwise it uses synchronous updates. On stream stop it disables dual crop and resizer with asynchronous update semantics.

## State And Persistence

Persistent state is in `struct rkisp1_resizer`: path id, RKISP1 device pointer, register base, config pointer, pads, and V4L2 subdev state. Active format/crop state is managed by the V4L2 subdev state framework. Hardware state is held in RSZ and dual-crop registers and shadowed until update bits are asserted. There is no disk persistence.

## Dependencies And Integration Points

The file integrates with media-controller subdev registration, V4L2 subdev pad state, RKISP1 media-bus format helpers from `rkisp1-common.h`, capture format enumeration through `rkisp1_cap_enum_mbus_codes()`, feature detection through `rkisp1_has_feature()`, and register definitions from `rkisp1-regs.h`. It sits between the ISP output and capture devices in the media pipeline.

## Risks

Scaling math can fail if dimensions become invalid; callers must keep widths and heights above one because ratio calculation subtracts one. YUV chroma divisors must match the negotiated media-bus code or chroma scaling will be wrong. Raw mainpath and selfpath constraints are asymmetric, so overly broad format propagation can expose unsupported paths. Shadow update timing matters when both paths stream concurrently. Crop alignment and bounds adjustment are important because odd YUV crop positions can break chroma alignment.

## Test Signals

Useful tests include media-ctl topology validation, format enumeration on mainpath and selfpath sink/source pads, YUV422 to YUV420 conversion, identity scaling that disables the resizer, downscale/upscale ratio programming, crop bounds and even alignment, Bayer mainpath crop rejection, no-dual-crop hardware behavior, dual-path streaming order changes, and stream stop cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-resizer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-stats.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-stats.c

## Purpose

`rkisp1-stats.c` implements the RKISP1 statistics metadata capture video node. It lets userspace queue buffers that are filled from ISP 3A measurement registers when statistics-related interrupts fire. The file reports AWB, AEC, AFM, histogram, and BLS measurements in `V4L2_META_FMT_RK_ISP1_STAT_3A` buffers.

## Important APIs, Types, And Functions

The V4L2 metadata surface is implemented by `rkisp1_stats_enum_fmt_meta_cap()`, `rkisp1_stats_g_fmt_meta_cap()`, `rkisp1_stats_querycap()`, `rkisp1_stats_ioctl`, and `rkisp1_stats_fops`. Buffer management is implemented by `rkisp1_stats_vb2_queue_setup()`, `rkisp1_stats_vb2_buf_queue()`, `rkisp1_stats_vb2_buf_prepare()`, `rkisp1_stats_vb2_stop_streaming()`, and `rkisp1_stats_init_vb2_queue()`.

Measurement readers include `rkisp1_stats_get_awb_meas_v10/v12()`, `rkisp1_stats_get_aec_meas_v10/v12()`, `rkisp1_stats_get_afc_meas()`, `rkisp1_stats_get_hst_meas_v10/v12()`, and `rkisp1_stats_get_bls_meas()`. `rkisp1_v10_stats_ops` and `rkisp1_v12_stats_ops` select version-specific readers. `rkisp1_stats_send_measurement()` fills a queued buffer, while `rkisp1_stats_isr()` is the interrupt entry point.

## Control Flow

Registration initializes a metadata capture queue, sets the only format to `V4L2_META_FMT_RK_ISP1_STAT_3A`, initializes the ops table according to `isp_ver`, creates one sink media pad, and registers the video device. Userspace allocates two to eight vmalloc-backed buffers, prepares them with enough space for `struct rkisp1_stat_buffer`, and queues them to `stats->stat`.

When the ISP interrupt handler calls `rkisp1_stats_isr(stats, isp_ris)`, this file clears measurement interrupts by writing `RKISP1_STATS_MEAS_MASK` to `RKISP1_CIF_ISP_ICR`, checks whether measurement MIS bits remain set and increments `debug.stats_error` if so, then fills one queued buffer if `isp_ris` contains measurement bits. Each interrupt bit gates a specific reader: AWB done reads AWB registers, AFM finish reads focus sums and luma, exposure end reads AEC means and BLS measured values, and histogram ready reads histogram bins. The completed buffer gets payload size, frame sequence, timestamp, and `VB2_BUF_STATE_DONE`.

## State And Persistence

Runtime state lives in `struct rkisp1_stats`: the queued buffer list, spinlock, selected stats ops, video node, and RKISP1 device pointer. The data delivered to userspace is transient and tied to the ISP frame sequence and interrupt status. There is no persistence outside queued buffers and hardware measurement registers. Stop streaming drains queued buffers with `VB2_BUF_STATE_ERROR`.

## Dependencies And Integration Points

This file depends on V4L2 metadata capture, videobuf2 vmalloc memory, media entity registration, RKISP1 register helpers, `rkisp1-regs.h` measurement register definitions, and `rkisp1_bls_swap_regs()` for Bayer-order-aware BLS value mapping. It integrates with params configuration because params determine AWB/AEC/HST/AFM windows and enable bits, and it integrates with the top-level ISP ISR through `rkisp1_stats_isr()`.

## Risks

The ISR silently drops statistics if no userspace buffer is queued. Packed v12 AEC and histogram reads depend on exact field extraction macros. `rkisp1_stats_get_bls_meas()` relies on the current ISP sink format and Bayer pattern to swap measured channels correctly. The code contains comments questioning concurrent register access from ISR context, so changes that read or write the same measurement registers elsewhere need locking scrutiny. The current stop-streaming loop is bounded by the maximum buffer count; that matches queue setup but should remain aligned if buffer limits change.

## Test Signals

Good signals include metadata format enumeration, buffer size validation, streaming with and without queued buffers, interrupt-driven completion for each measurement bit, v10 and v12 histogram/AEC packing checks, BLS channel ordering across Bayer patterns, timestamp and sequence correctness, `stats_error` behavior when MIS bits remain set, and stop-streaming buffer error completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/Kconfig

## Purpose

`rkvdec/Kconfig` declares the kernel configuration option for the Rockchip video decoder driver. It controls whether the mem2mem V4L2 decoder for Rockchip decoder IP is built into the kernel, built as a module, or omitted.

## Important APIs, Types, And Symbols

The only symbol defined is `VIDEO_ROCKCHIP_VDEC`, a tristate named "Rockchip Video Decoder driver". It depends on `ARCH_ROCKCHIP || COMPILE_TEST` and `VIDEO_DEV`. It selects `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, `V4L2_H264`, and `V4L2_VP9`.

## Control Flow

Kconfig evaluation exposes the option when the architecture or compile-test condition is satisfied and video-device support is enabled. If selected as module, the help text states that the module name is `rockchip-vdec`. The Makefile then consumes `CONFIG_VIDEO_ROCKCHIP_VDEC` to build the object list.

## State And Persistence

The file has no runtime state. The selected tristate value persists only in the kernel build configuration and determines which objects are compiled and linked.

## Dependencies And Integration Points

The option integrates with the Linux media subsystem, V4L2 mem2mem framework, videobuf2 memory allocators, codec control helpers for H.264 and VP9, and Rockchip architecture builds. It is consumed directly by the adjacent `Makefile`.

## Risks

Missing selects can cause link failures or unusable decoder registration. Over-selecting codec helpers can increase build surface. The config currently selects H.264 and VP9 helpers while the Makefile also builds HEVC-specific objects; HEVC support may rely on common media infrastructure not selected here or on symbols selected elsewhere.

## Test Signals

Useful signals include `allyesconfig`, `allmodconfig`, `COMPILE_TEST` builds on non-Rockchip architectures, module build verification for `rockchip-vdec`, and boot-time/media-device registration tests on Rockchip hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/Makefile

## Purpose

`rkvdec/Makefile` maps `CONFIG_VIDEO_ROCKCHIP_VDEC` to the Rockchip video decoder module object and lists the compilation units that make up the driver. It is the build-system counterpart to `rkvdec/Kconfig`.

## Important APIs, Types, And Symbols

`obj-$(CONFIG_VIDEO_ROCKCHIP_VDEC) += rockchip-vdec.o` declares the top-level module/object. `rockchip-vdec-y` aggregates `rkvdec.o`, `rkvdec-cabac.o`, `rkvdec-h264.o`, `rkvdec-h264-common.o`, `rkvdec-hevc.o`, `rkvdec-hevc-common.o`, `rkvdec-rcb.o`, `rkvdec-vdpu381-h264.o`, `rkvdec-vdpu381-hevc.o`, `rkvdec-vdpu383-h264.o`, `rkvdec-vdpu383-hevc.o`, and `rkvdec-vp9.o`.

## Control Flow

There is no runtime control flow. During kbuild evaluation, the selected config value decides whether `rockchip-vdec.o` is built. The `rockchip-vdec-y` list causes kbuild to compile and link the core decoder, CABAC table/support code, codec-specific H.264/HEVC/VP9 code, reference-compressed-buffer support, and VDPU381/VDPU383 variant implementations into one driver object.

## State And Persistence

The Makefile has no runtime state. Build state is represented by generated object files and the final built-in or module artifact.

## Dependencies And Integration Points

It integrates with the Linux kbuild composite-object convention, the adjacent Kconfig symbol, and all source files in the `rkvdec` directory. The object names imply integration across a common decoder core, codec common layers, per-codec operations, and hardware-generation-specific backends.

## Risks

Adding or removing source files without updating this list can create unresolved symbols or dead code. Codec support is built as one composite object rather than independently toggled, so compile failures in any codec or hardware variant can break the whole driver. The object list must stay in dependency order where link ordering matters for built-in initialization or weak/common symbol resolution.

## Test Signals

Useful signals include incremental builds after touching any listed source file, module builds with `CONFIG_VIDEO_ROCKCHIP_VDEC=m`, built-in builds with `=y`, `COMPILE_TEST` builds, and link checks that cover all H.264, HEVC, VP9, VDPU381, and VDPU383 object references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/Makefile -->
