# sources/distributed-fs/ceph-client/include/media/v4l2-mc.h

Purpose: declares V4L2/media-controller integration helpers for graph creation, exclusive media-source ownership, firmware-node link creation, and deprecated pipeline power-management helpers.

Important APIs/types: with `CONFIG_MEDIA_CONTROLLER`, APIs include `v4l2_mc_create_media_graph()`, `v4l_enable_media_source()`, `v4l_disable_media_source()`, `v4l_vb2q_enable_media_source()`, `v4l2_create_fwnode_links_to_pad()`, `v4l2_create_fwnode_links()`, `v4l2_pipeline_pm_get()`, `v4l2_pipeline_pm_put()`, and `v4l2_pipeline_link_notify()`. Without media-controller support, no-op stubs are provided for graph/source/pipeline-PM helpers, but not for the fwnode link creation helpers.

Control flow: bridge drivers can create generic PC-consumer media graphs, V4L2/DVB core paths can enable/disable a shared media source before source-changing operations, and async notifier bound callbacks can translate firmware endpoint connections into media links. Deprecated pipeline PM helpers update entity use counts around opens/releases and link changes.

State and persistence: persistent state lives in `media_device`, `media_entity`, media links, source-enable callbacks, and vb2 queues. The helper declarations do not own state directly.

Dependencies and integration: includes `media-device.h`, `v4l2-dev.h`, `v4l2-subdev.h`, and Linux types. It integrates V4L2 video nodes, subdevices, firmware endpoint parsing, media graph links, and vb2 queues.

Risks: `v4l2_mc_create_media_graph()` is intentionally too simple for subdev-centric camera pipelines; enabled link flags can be invalid if multiple fwnode links are created; sink subdevices must implement `.get_fwnode_pad`; deprecated pipeline PM should not be used in new drivers; and the lack of disabled-config stubs for fwnode link helpers means call sites must be config-gated or rely on media-controller builds.

Test signals: graph creation for tuner/decoder/video entities, exclusive source enable conflicts, vb2 queue to video-device lookup, fwnode link creation to a pad and to a sink subdev, multiple-link flag validation, disabled-config stub compilation, and deprecated PM get/put/link-notify balance in legacy drivers.
