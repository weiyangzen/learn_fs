# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-common.h

Purpose: central data model for the Rockchip CIF driver. It defines constants, enum namespaces, format descriptors, stream/interface/device structures, and SoC match-data structures shared by DVP, MIPI, interface, stream, and platform modules.

Important APIs/types/functions: `RKCIF_DRIVER_NAME`, `RKCIF_CLK_MAX`, format/interface/id enums, `struct rkcif_buffer`, `struct rkcif_dummy_buffer`, `struct rkcif_input_fmt`, `struct rkcif_output_fmt`, `struct rkcif_remote`, `struct rkcif_stream`, `struct rkcif_interface`, `struct rkcif_mipi_match_data`, `struct rkcif_dvp_match_data`, `struct rkcif_match_data`, and `struct rkcif_device`. `struct rkcif_stream` contains ping-pong buffers, frame counters, stop waitqueue, vb2 queue, video device, and hardware hooks. `struct rkcif_interface` represents a V4L2 subdev bridge with sink/source pads, endpoint data, stream array, input formats, and optional crop callback.

Control flow: platform probe fills `struct rkcif_device` from match data, DVP/MIPI registration fills `struct rkcif_interface` and `struct rkcif_stream`, stream registration exposes video nodes, and the interface subdev propagates format/routing/crop state between remote sensors/receivers and stream nodes.

State and persistence: this header defines all persistent in-kernel runtime state for CIF. State includes media graph objects, async notifier links, clocks/reset/regmap/base address, active streams, queued buffers, dummy DMA storage, and match-data pointers. There is no filesystem persistence.

Dependencies/integration: includes Linux clocks/mutex/regmap and V4L2/media/vb2 headers plus `rkcif-regs.h`. It is the type contract among all files in this subset.

Risks: broad shared structs mean layout changes can ripple across all CIF modules. The `union` fields in format descriptors and interfaces require callers to respect whether a stream is DVP or MIPI. The `RKCIF_ID_MAX` and `RKCIF_IF_MAX` enum sizes drive fixed arrays; adding hardware instances requires careful array and routing updates.

Test signals: compile coverage across all CIF modules, probe of both PX30 and RK3568 match data, media graph enumeration, multi-stream MIPI routing, DVP single-stream behavior, and vb2 queue lifecycle.
