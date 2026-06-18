# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-stream.h

Purpose: internal header for the CIF DMA stream/video-node abstraction.

Important APIs/types/functions: declares `rkcif_stream_pingpong()`, `rkcif_stream_register()`, `rkcif_stream_unregister()`, and `rkcif_stream_find_output_fmt()`. The file comment describes each stream as a V4L2 capture device with a sink pad connected to an interface/crop subdev and a ping-pong DMA scheme.

Control flow: DVP/MIPI modules install callbacks and call `rkcif_stream_register()`; their ISRs call `rkcif_stream_pingpong()`; unregister paths call `rkcif_stream_unregister()`.

State and persistence: no state in the header; per-stream state is in `struct rkcif_stream`.

Dependencies/integration: bridges `rkcif-stream.c` to DVP/MIPI modules and shared common types.

Risks: exported behavior assumes hardware modules provide compatible callbacks for queueing, start, and stop. Header comments should stay aligned with the media graph design.

Test signals: compile/link and media graph validation with stream video nodes connected to interface source pads.
