# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-interface.c

Purpose: V4L2 subdev abstraction for CIF input interfaces and crop units. It bridges a remote sensor or CSI receiver on a sink pad to one or more DMA stream video nodes on a source pad, handling media-bus format propagation, stream routing, crop state, and upstream stream enable/disable.

Important APIs/types/functions: exports `rkcif_interface_register()`, `rkcif_interface_unregister()`, and `rkcif_interface_find_input_fmt()`. Key callbacks are `rkcif_interface_set_fmt()`, `get/set_selection`, `set_routing`, `enable_streams`, `disable_streams`, and `init_state`. It uses `V4L2_SUBDEV_FL_STREAMS` and validates routes as one-to-one with source streams below `RKCIF_ID_MAX`.

Control flow: registration initializes the subdev, pads, default state, and device registration, then `rkcif_interface_add()` parses the DT endpoint for the interface index, validates DVP bus type, reads optional DVP clock delay, adds the remote endpoint to the async notifier, and marks the interface active. Format setting is sink-driven: source format always mirrors sink format and crop is reset to the full new size. Crop is only exposed on the source pad. Stream enable first applies crop to hardware through the interface callback, translates source stream masks to sink streams, then enables the upstream remote subdev stream. Disable translates and disables upstream streams.

State and persistence: active format/crop/routing state is in V4L2 subdev state. `struct rkcif_interface` stores endpoint parse data, remote async connection, status, stream array, input format table, and optional crop callback. No persistent storage.

Dependencies/integration: relies on media-controller pad links, V4L2 subdev state/routing helpers, fwnode endpoint parsing, V4L2 async notifier in `rkcif-dev.c`, and hardware crop callbacks from DVP/MIPI modules.

Risks: `media_pad_remote_pad_first()` in stream enable/disable assumes a connected remote pad; bad media graph setup can lead to null/invalid use. Crop is copied directly from userspace selection and only adjusted indirectly by users of the source format, so invalid crop dimensions could produce hardware programming mismatches unless bounded by V4L2 helpers/userspace discipline. DVP has one crop for all IDs and uses stream ID0, while MIPI applies crop per active route; route mistakes can program the wrong stream.

Test signals: subdev format propagation sink to source, crop get/set/default/bounds, stream routing with MIPI IDs, DVP crop shared behavior, async endpoint parsing for DVP and MIPI ports, and upstream sensor stream-on/off ordering.
