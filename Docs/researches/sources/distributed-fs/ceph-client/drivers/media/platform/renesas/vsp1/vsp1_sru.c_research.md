# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_sru.c

Purpose: implements the Super Resolution Unit entity, a scaler/sharpener that can pass through or upscale by 2x in both dimensions. It exposes a V4L2 subdevice with an intensity control and programs SRU parameters into display lists.

Important APIs/functions: `vsp1_sru_create()` allocates/registers the SRU. `sru_set_format()` and `sru_try_format()` clamp pad formats and propagate sink to source while enforcing no format conversion. `sru_enum_frame_size()` advertises source sizes as either same-as-input or 2x when the input is small enough. `sru_configure_stream()` writes `VI6_SRU_CTRL0/1/2` based on input format, upscale mode, and intensity. `sru_max_width()` and `sru_partition()` integrate the SRU into the partition algorithm.

Control flow/state: the custom `V4L2_CID_VSP1_SRU_INTENSITY` stores `sru->intensity` from 1 to 6, indexing fixed parameter tables. Source pad sizing compares requested output area against input area and chooses either no scale or exact 2x. Partition propagation halves the downstream window when SRU x2 is active.

Dependencies/integration: uses VSP1 entity helpers, V4L2 subdev state, `vsp1_pipe` partition state, and `vsp1_regs` SRU register fields. It supports ARGB8888 and AYUV media-bus codes and registers as `MEDIA_ENT_F_PROC_VIDEO_SCALER`.

Risks and test signals: the area threshold in `sru_try_format()` controls whether scaling is enabled and can affect user expectations. Partition limits reserve overlap room, so large-frame slicing should be tested with and without scaling. Validate all six intensity settings, RGB/YUV inputs, pad propagation, maximum-size boundaries, and visual output for 2x upscale.
