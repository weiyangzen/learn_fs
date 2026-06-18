# Research: sources/distributed-fs/ceph-client/drivers/media/platform/video-mux.c

Purpose: implements a generic V4L2 media-controller subdevice for a device-tree `video-mux` whose active input is selected through the Linux mux-control consumer API. It presents N-1 sink pads and one source pad, propagates formats from the enabled sink to the source, and forwards stream control upstream.

Important types and APIs: `struct video_mux` owns a `v4l2_subdev`, async notifier, media pads, `struct mux_control`, mutex, and `active` sink index. Key functions are `video_mux_probe/remove`, `video_mux_link_setup`, `video_mux_s_stream`, `video_mux_set_format`, `video_mux_init_state`, and `video_mux_async_register`. It integrates with `media_entity_operations`, V4L2 subdev pad/video ops, `v4l2_create_fwnode_links`, `v4l2_async_nf_add_fwnode_remote`, and `devm_mux_control_get`.

Control flow: probe counts graph endpoints and treats the largest numbered port as the output, allocates pads, initializes the subdev, finalizes active state, then registers an async notifier for connected input endpoints. Link setup is the main state transition: enabling a sink link calls `mux_control_try_select`, rejects a different active sink with `-EBUSY`, records `active`, and copies that sink format to the source pad; disabling the active sink deselects the mux and sets `active = -1`. Streaming requires an active sink, finds the remote upstream subdevice, and calls its `video.s_stream`.

State and persistence: runtime state is only in memory and the mux-control hardware selection. Active-pad and format state are protected by the mux mutex plus V4L2 subdev active-state locking. There is no persistent userspace state.

Dependencies and integration: requires OF graph endpoints, a mux provider, V4L2 subdev/media-controller APIs, async notifier binding, and accepted media bus codes. It is selected by platform OF compatible `video-mux`.

Risks: source-pad link toggles intentionally do not affect selection, so userspace must enable exactly one sink link. Format propagation only mirrors the active sink; inactive sink formats can diverge. Streaming fails if the remote pad is missing or not a V4L2 subdev. Test signals include `media-ctl` link enable/disable behavior, `v4l2-compliance` subdev format operations, format mirroring on active input changes, and mux-control provider error injection.
