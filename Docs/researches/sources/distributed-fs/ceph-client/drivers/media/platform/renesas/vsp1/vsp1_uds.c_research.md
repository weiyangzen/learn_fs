# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uds.c

Purpose: implements the Up/Down Scaler entity. It provides V4L2 pad negotiation for ARGB/YUV scaling, computes fixed-point scaling ratios and passband filter widths, configures alpha scaling, and participates in partitioned frame processing.

Important APIs/functions: `vsp1_uds_create()` registers an indexed UDS subdevice. `vsp1_uds_set_alpha()` programs the fixed alpha output value used when alpha scaling is disabled. `uds_output_limits()`, `uds_compute_ratio()`, and `uds_passband_width()` implement hardware scaling calculations. `uds_set_format()`/`uds_try_format()` handle pad format negotiation. Entity callbacks configure stream registers, clip per partition, report max width, and map downstream partition windows back to UDS input windows.

Control flow/state: sink format is clamped to 4..8190 and color-normalized. Source format keeps the sink code/colorspace and clamps width/height to limits derived from U4.12 ratio range. `uds_configure_stream()` computes horizontal/vertical scale, disables multitap when alpha scaling and strong downscale conflict, writes control, passband, and scale registers. `uds_partition()` maps output window coordinates to input coordinates and updates the upstream window.

Dependencies/integration: driven by `vsp1_video_setup_pipeline()` for `scale_alpha` based on upstream alpha/BRx state and by `vsp1_pipeline_propagate_alpha()` for fixed alpha. It depends on VSP1 display-list writes, V4L2 subdev state, and partition helpers.

Risks and test signals: `uds_compute_ratio()` is explicitly approximate, so edge scaling ratios can be sensitive. Division assumes valid nonzero output dimensions enforced by format constraints. Test min/max sizes, strong downscale with alpha, RGB/YUV propagation, passband values, multi-partition scaling, and UDS after BRU/BRS where alpha should be fixed at 255.
