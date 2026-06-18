
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-resizer.c

## Purpose

`c3-isp-resizer.c` implements three ISP resizer/scaler V4L2 subdevices. Each resizer receives one ISP core video source, supports crop and compose selection on its sink pad, programs display-path crop/output/PPS scaling hardware, and forwards the stream to the corresponding capture node.

## Important APIs, Types, And Functions

`struct c3_isp_rsz_format_info` lists RAW16 Bayer and YUV10 formats accepted on both sink and source pads. `struct c3_isp_pps_io_size` captures the scaler input/output geometry used by `c3_isp_rsz_pps_size()`. `c3_isp_pps_lut` is a 33-entry four-tap coefficient table written for luma and chroma.

Scaler helpers are `c3_isp_rsz_pps_size()`, `c3_isp_rsz_pps_lut()`, `c3_isp_rsz_pps_disable()`, and `c3_isp_rsz_pps_enable()`. Stream helpers `c3_isp_rsz_start()` and `c3_isp_rsz_stop()` choose raw MIPI output versus core output, program input size, crop, output size, and path enable bits. Public registration functions are `c3_isp_resizers_register()` and `c3_isp_resizers_unregister()`.

V4L2 subdev operations include media-bus code enumeration, format get/set, selection get/set, and stream enable/disable. `c3_isp_rsz_init_state()` seeds default YUV10 1920x1080-style state.

## Control Flow

Sink format setting validates the requested code, clamps dimensions, resets crop to full frame, resets compose to crop, and mirrors the source format dimensions. Source format setting is derived from sink code and compose size; callers cannot independently choose a different source code.

Selection control supports crop and compose only on the sink pad. Crop is clamped inside the sink frame and aligned to even dimensions. Compose is clamped inside crop size, aligned to even dimensions, and updates the source pad dimensions. At stream enable, the resizer programs path source selection based on whether input is raw, writes crop registers, enables crop, enables PPS scaling for non-raw input if compose differs from crop, writes output size, enables the selected display path, pre-configures params and stats, then enables its upstream core source stream. Disable reverses the display path and disables upstream core stream.

## State And Persistence

Each `struct c3_isp_resizer` stores its ID, parent ISP pointer, source subdev pointer, source pad index, pads, and subdev state. Crop/compose/format state persists in the V4L2 subdev active state while the device exists. Hardware state is volatile and reprogrammed on each start.

## Dependencies And Integration Points

The file depends on the ISP core for upstream streaming, the capture devices for downstream links, C3 register helpers, media-controller validation, and V4L2 subdev selection APIs. It invokes `c3_isp_params_pre_cfg()` and `c3_isp_stats_pre_cfg()` as part of stream start, making resizer start the point where metadata processing and stats DMA are primed.

## Risks

`c3_isp_rsz_set_source_fmt()` dereferences `rsz_fmt` without checking for NULL; it is safe only if source code is always derived from a validated sink code. PPS scaling calculations divide by output width/height, so selection clamping must prevent zero dimensions. The pre-scaler rate and tap-selection logic is hardware-specific and has several threshold branches, especially for `C3_ISP_RSZ_2`; off-by-one geometry can produce bad scaling or line-buffer overflow. Raw paths skip PPS but still program output size, so raw resize requests are effectively crop/pass-through rather than scale.

## Test Signals

Exercise `VIDIOC_SUBDEV_S_SELECTION` for crop/compose bounds, odd sizes, minimum sizes, and source-pad rejection. Verify media-bus enumeration for RAW16 and YUV10. Hardware tests should compare register programming for no-scale, simple downscale, downscale over 4x, large-width paths, and raw-vs-YUV input selection. Streaming tests should confirm params/stats pre-configuration happens before frame IRQs and that each resizer controls the matching capture path.
