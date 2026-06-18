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
