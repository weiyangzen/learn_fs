# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mc.c

## Purpose
`v4l2-mc.c` contains V4L2 helpers for media-controller graph construction, fwnode-based link creation, media-source enable/disable callbacks, vb2 source activation, and legacy pipeline power management.

## Important APIs, Types, And Functions
Exports include `v4l2_mc_create_media_graph()`, `v4l_enable_media_source()`, `v4l_disable_media_source()`, `v4l_vb2q_enable_media_source()`, `v4l2_create_fwnode_links_to_pad()`, `v4l2_create_fwnode_links()`, `v4l2_pipeline_pm_get()`, `v4l2_pipeline_pm_put()`, and `v4l2_pipeline_link_notify()`. The file operates on `struct media_device`, `struct media_entity`, `struct media_link`, `struct video_device`, `struct vb2_queue`, and `struct v4l2_subdev`.

## Control Flow
`v4l2_mc_create_media_graph()` scans entities by function, discovers tuners, IF decoders, analog decoders, connectors, video/VBI/software-radio I/O nodes, and camera sensors, then creates enabled pad links for webcam or analog-TV style graphs. Fwnode helpers iterate source endpoints, map local source pads and remote sink pads, skip existing links, and call `media_create_pad_link()`. Source enable/disable helpers serialize through `mdev->graph_mutex` and call media-device callbacks when present. Pipeline PM helpers walk the graph, count open video nodes, and call subdev `core.s_power` on 0-to-nonzero and nonzero-to-0 transitions.

## State And Persistence
The persistent state modified here is in media-controller graph objects: pad links, entity `use_count`, video pipeline fields, and optional device-specific source ownership. No data is stored outside kernel objects. Graph and power changes are protected by `graph_mutex`, while graph walks use `mdev->pm_count_walk`.

## Dependencies And Integration Points
This file depends on the media entity/link API, V4L2 file handles, V4L2 subdev calls, videobuf2 queues, fwnode graph helpers, and optional media-device callbacks. It is used by bridge drivers that expose media-controller topology without manually wiring every common link pattern.

## Risks And Test Signals
Graph construction is sensitive to correct entity functions, pad flags, and `PAD_SIGNAL_*` annotations. Pipeline PM can miscount if link notifications and open/close paths are not paired. Tests should build representative webcam, tuner+IF+decoder, connector, VBI, and SDR graphs; verify duplicate fwnode links are skipped; exercise source enable contention returning `-EBUSY`; and validate power rollback when a subdev `s_power(1)` fails partway through a graph walk.
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mc.c

## Purpose
`v4l2-mc.c` contains V4L2 helpers for media-controller graph construction, fwnode-based link creation, media-source enable/disable callbacks, vb2 source activation, and legacy pipeline power management.

## Important APIs, Types, And Functions
Exports include `v4l2_mc_create_media_graph()`, `v4l_enable_media_source()`, `v4l_disable_media_source()`, `v4l_vb2q_enable_media_source()`, `v4l2_create_fwnode_links_to_pad()`, `v4l2_create_fwnode_links()`, `v4l2_pipeline_pm_get()`, `v4l2_pipeline_pm_put()`, and `v4l2_pipeline_link_notify()`. The file operates on `struct media_device`, `struct media_entity`, `struct media_link`, `struct video_device`, `struct vb2_queue`, and `struct v4l2_subdev`.

## Control Flow
`v4l2_mc_create_media_graph()` scans entities by function, discovers tuners, IF decoders, analog decoders, connectors, video/VBI/software-radio I/O nodes, and camera sensors, then creates enabled pad links for webcam or analog-TV style graphs. Fwnode helpers iterate source endpoints, map local source pads and remote sink pads, skip existing links, and call `media_create_pad_link()`. Source enable/disable helpers serialize through `mdev->graph_mutex` and call media-device callbacks when present. Pipeline PM helpers walk the graph, count open video nodes, and call subdev `core.s_power` on 0-to-nonzero and nonzero-to-0 transitions.

## State And Persistence
The persistent state modified here is in media-controller graph objects: pad links, entity `use_count`, video pipeline fields, and optional device-specific source ownership. No data is stored outside kernel objects. Graph and power changes are protected by `graph_mutex`, while graph walks use `mdev->pm_count_walk`.

## Dependencies And Integration Points
This file depends on the media entity/link API, V4L2 file handles, V4L2 subdev calls, videobuf2 queues, fwnode graph helpers, and optional media-device callbacks. It is used by bridge drivers that expose media-controller topology without manually wiring every common link pattern.

## Risks And Test Signals
Graph construction is sensitive to correct entity functions, pad flags, and `PAD_SIGNAL_*` annotations. Pipeline PM can miscount if link notifications and open/close paths are not paired. Tests should build representative webcam, tuner+IF+decoder, connector, VBI, and SDR graphs; verify duplicate fwnode links are skipped; exercise source enable contention returning `-EBUSY`; and validate power rollback when a subdev `s_power(1)` fails partway through a graph walk.
