# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-subdev.c

Purpose: implements the RZ/V2H(P) IVC V4L2 subdevice that sits between the video-output node and downstream raw-processing hardware. It exposes a two-pad pixel formatter media entity, maps 8/10/12/14/16/20-bit Bayer sink formats to fixed 20-bit Bayer source formats, and registers the associated video device once the subdevice is registered.

Important APIs and functions: `rzv2h_ivc_enum_mbus_code()`, `rzv2h_ivc_enum_frame_size()`, `rzv2h_ivc_set_fmt()`, `rzv2h_ivc_init_state()`, `rzv2h_ivc_registered()`, `rzv2h_ivc_link_validate()`, `rzv2h_ivc_initialise_subdevice()`, and `rzv2h_ivc_deinit_subdevice()`. The file defines `rzv2h_ivc_pad_ops`, `rzv2h_ivc_subdev_ops`, internal ops, and `media_entity_operations`.

Control flow: format enumeration distinguishes source and sink pads. Sink pad format changes are clamped to IVC min/max dimensions, default to a supported Bayer code when needed, then propagate to the source pad with the matching 20-bit output code. Stream enable/disable intentionally do nothing because power and register programming are driven by the video node's streamon path. Registration finalizes the subdev, async-registers it, and later creates the video device through the internal `registered` callback.

State and persistence: persistent state is held in the V4L2 subdev active state and in `ivc->format` for the video node. Link validation compares active subdev dimensions and media-bus code against the selected video pixel format. Cleanup removes links, unregisters the subdev, frees subdev state, and cleans the media entity.

Dependencies and integration: depends on `rzv2h-ivc.h`, V4L2 subdev/event/control helpers, media entity pads, and async subdev registration. It integrates with `rzv2h-ivc-video.c` through `rzv2h_ivc_init_vdev()` and validates media links created from the video output node to the IVC subdevice.

Risks and test signals: risk centers on code mapping mismatches between video fourcc formats and subdev Bayer codes, invalid width/height propagation, and cleanup order. Test with `media-ctl -p`, format enumeration on both pads, `VIDIOC_S_FMT` plus `media-ctl --set-v4l2`, link validation failures for incompatible Bayer order, and streamon/streamoff through the video node.
