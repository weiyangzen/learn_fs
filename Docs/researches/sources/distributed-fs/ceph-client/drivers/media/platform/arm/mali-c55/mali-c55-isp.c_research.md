# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-isp.c

Purpose: Implements the Mali-C55 ISP V4L2 subdevice: supported sink/source media-bus formats, crop handling, stream start/stop, frame-sync events, capabilities control, subdev registration, and ISP configuration startup.

Important APIs/functions: Exports ISP format lookup helpers, `mali_c55_isp_queue_event_sof()`, `mali_c55_register_isp()`, and `mali_c55_unregister_isp()`. Internal operations implement enum/set/get format, crop selection, stream enable/disable, event subscription, init state, and read-only capabilities control.

Control flow: Format setup accepts raw 20-bit Bayer or RGB bypass input at the sink, propagates processed RGB121212 to the main source and sink format to bypass. Stream enable resolves the active remote source pad, resets frame sequence, initializes/defaults ISP config through params code, writes ping config, starts safe-start mode, then enables the upstream source stream. Stream disable disables upstream and safe-stops the ISP.

State and persistence: ISP state stores media pads, remote source pointer, capture lock shared by streaming users, frame sequence, and control handler. Active formats/crops live in V4L2 subdev state.

Dependencies and integration: Integrates with params initialization, core register helpers, V4L2 subdev streams/events, media routing, TPG or external sensor source, resizers, stats, and params nodes.

Risks: `media_pad_remote_pad_unique()` is assumed to return a usable remote pad; invalid graph state could dereference null. Some source color metadata maps from sink colorspace unexpectedly. Only one input stream is supported.

Test signals: Subdev pad format/crop compliance, TPG and external sensor stream starts, source-change through route switching, frame-sync event sequence, capabilities control readback, and invalid link graph handling.
