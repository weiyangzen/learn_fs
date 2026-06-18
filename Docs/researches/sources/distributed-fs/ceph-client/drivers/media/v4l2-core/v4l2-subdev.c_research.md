# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev.c

## Purpose
`v4l2-subdev.c` implements the V4L2 subdevice core: subdev devnode file operations, ioctl dispatch, pad-operation validation wrappers, active/try state allocation, media-controller link validation, routing and stream-state helpers, event notification, initialization, cleanup, and privacy LED ownership.

## Important APIs, Types, And Functions
Important exports include `v4l2_subdev_call_wrappers`, `v4l2_subdev_fops`, `v4l2_subdev_link_validate_default()`, `v4l2_subdev_link_validate()`, state allocation/free/finalize/cleanup helpers, state accessors for format/crop/compose/interval, routing helpers, stream enable/disable helpers, `v4l2_subdev_s_stream_helper()`, frame-descriptor passthrough helpers, `v4l2_subdev_init()`, `v4l2_subdev_notify_event()`, `v4l2_subdev_is_streaming()`, and privacy LED get/put. Internal `struct v4l2_subdev_stream_config` stores per-pad/per-stream format, crop, compose, interval, and enabled state.

## Control Flow
When the subdev API is enabled, `subdev_open()` allocates a file-handle state, initializes a V4L2 fh, pins the media-device owner, and calls internal open hooks. Ioctls enter through `video_usercopy()`, take the video-device lock, select active or try state based on command and `which`, lock that state, and dispatch controls, events, pad format/selection/frame interval, EDID, DV timings, standards, routing, and client capabilities. Pad wrapper functions validate `which`, pad index, stream availability, and state before calling driver ops. Link validation compares stream masks and source/sink formats, delegating to video-device validation when needed. Stream helpers validate source pads, stream masks, duplicate enable/disable, then call modern `.enable_streams()`/`.disable_streams()` or legacy `.s_stream()` fallback.

## State And Persistence
Persistent runtime state is held in `struct v4l2_subdev`: active state, optional shared state lock, enabled pads, legacy `s_stream_enabled`, event flags, privacy LED pointer, async endpoint list, and media entity metadata. `struct v4l2_subdev_state` owns legacy pad configs or streams API routing/config arrays. State allocation may call driver `internal_ops->init_state()`. Cleanup frees active state and async endpoint records. Privacy LED ownership disables sysfs access while held and toggles brightness during streaming.

## Dependencies And Integration Points
The file depends on V4L2 controls, events, file handles, ioctl helpers, media-controller entities and pads, fwnode matching, LED class support, and driver-supplied subdev ops. It forms the main integration layer between userspace subdev devnodes, bridge drivers, sensor drivers, routing-aware subdevs, and media graph validation.

## Risks And Test Signals
Risks cluster around ioctl permission checks, active versus try state locking, experimental streams API gating, route validation limits, stream enable/disable idempotency, and legacy `.s_stream()` compatibility. Tests should cover read-only devnodes rejecting active setters, stream-cap negotiation, routing copy-in/copy-out and validation restrictions, link validation with dangling sink streams and mismatched formats, state accessors under legacy and streams modes, privacy LED acquisition/release with LED class variants, event polling, compat ioctl delegation, and cleanup after partially initialized subdevs.
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev.c

## Purpose
`v4l2-subdev.c` implements the V4L2 subdevice core: subdev devnode file operations, ioctl dispatch, pad-operation validation wrappers, active/try state allocation, media-controller link validation, routing and stream-state helpers, event notification, initialization, cleanup, and privacy LED ownership.

## Important APIs, Types, And Functions
Important exports include `v4l2_subdev_call_wrappers`, `v4l2_subdev_fops`, `v4l2_subdev_link_validate_default()`, `v4l2_subdev_link_validate()`, state allocation/free/finalize/cleanup helpers, state accessors for format/crop/compose/interval, routing helpers, stream enable/disable helpers, `v4l2_subdev_s_stream_helper()`, frame-descriptor passthrough helpers, `v4l2_subdev_init()`, `v4l2_subdev_notify_event()`, `v4l2_subdev_is_streaming()`, and privacy LED get/put. Internal `struct v4l2_subdev_stream_config` stores per-pad/per-stream format, crop, compose, interval, and enabled state.

## Control Flow
When the subdev API is enabled, `subdev_open()` allocates a file-handle state, initializes a V4L2 fh, pins the media-device owner, and calls internal open hooks. Ioctls enter through `video_usercopy()`, take the video-device lock, select active or try state based on command and `which`, lock that state, and dispatch controls, events, pad format/selection/frame interval, EDID, DV timings, standards, routing, and client capabilities. Pad wrapper functions validate `which`, pad index, stream availability, and state before calling driver ops. Link validation compares stream masks and source/sink formats, delegating to video-device validation when needed. Stream helpers validate source pads, stream masks, duplicate enable/disable, then call modern `.enable_streams()`/`.disable_streams()` or legacy `.s_stream()` fallback.

## State And Persistence
Persistent runtime state is held in `struct v4l2_subdev`: active state, optional shared state lock, enabled pads, legacy `s_stream_enabled`, event flags, privacy LED pointer, async endpoint list, and media entity metadata. `struct v4l2_subdev_state` owns legacy pad configs or streams API routing/config arrays. State allocation may call driver `internal_ops->init_state()`. Cleanup frees active state and async endpoint records. Privacy LED ownership disables sysfs access while held and toggles brightness during streaming.

## Dependencies And Integration Points
The file depends on V4L2 controls, events, file handles, ioctl helpers, media-controller entities and pads, fwnode matching, LED class support, and driver-supplied subdev ops. It forms the main integration layer between userspace subdev devnodes, bridge drivers, sensor drivers, routing-aware subdevs, and media graph validation.

## Risks And Test Signals
Risks cluster around ioctl permission checks, active versus try state locking, experimental streams API gating, route validation limits, stream enable/disable idempotency, and legacy `.s_stream()` compatibility. Tests should cover read-only devnodes rejecting active setters, stream-cap negotiation, routing copy-in/copy-out and validation restrictions, link validation with dangling sink streams and mismatched formats, state accessors under legacy and streams modes, privacy LED acquisition/release with LED class variants, event polling, compat ioctl delegation, and cleanup after partially initialized subdevs.
