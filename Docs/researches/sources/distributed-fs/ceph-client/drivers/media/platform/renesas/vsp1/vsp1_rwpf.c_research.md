# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rwpf.c

Purpose: implements the shared V4L2 subdevice operations and common controls for RPF and WPF pixel formatter entities. It handles media-bus code enumeration, frame-size enumeration, pad format propagation, RPF crop selection, and the alpha component control.

Important APIs/functions: `vsp1_rwpf_subdev_ops` exposes core and pad operations. `vsp1_rwpf_enum_mbus_code()` and `vsp1_rwpf_enum_frame_size()` describe RWPF source-pad capabilities, including the HSV no-conversion rule. `vsp1_rwpf_set_format()` clamps sink dimensions, normalizes colorspace fields, propagates sink to source, and accounts for WPF rotation. `vsp1_rwpf_get_selection()` and `vsp1_rwpf_set_selection()` implement RPF-only sink crop. `vsp1_rwpf_init_ctrls()` installs `V4L2_CID_ALPHA_COMPONENT`.

Control flow/state: sink format is the authoritative input format. On source pads, only code/encoding/quantization may change for RGB/YUV conversion, and V4L2 requires `V4L2_MBUS_FRAMEFMT_SET_CSC` before honoring requested encoding/quantization. For RPF crop, YUV rectangles are aligned to even coordinates/sizes, bounded to the sink format, then propagated to the source dimensions.

Dependencies/integration: common code is used by `vsp1_rpf_create()` and `vsp1_wpf_create()`. It relies on `vsp1_entity_get_state()`, `vsp1_entity_adjust_color_space()`, V4L2 subdev state helpers, and `vsp1_video` for WPF rotation queue-busy constraints.

Risks and test signals: accepting odd YUV crops can lead to invalid hardware, so link validation and video format alignment are important test signals. Source-pad CSC rules can surprise userspace. Rotation changes affect source dimensions and must be rejected while buffers are allocated. Test pad format set/get/try flows, HSV source restrictions, RGB/YUV CSC negotiation, RPF crop bounds/defaults, and alpha-control propagation into RPF/WPF programming.
