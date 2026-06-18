# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-crossbar.c

## Purpose
`imx8-isi-crossbar.c` implements the ISI input crossbar as a V4L2 subdevice with stream-aware routing. It routes external pixel-link inputs and a memory input to ISI pipeline source pads, validates routing constraints, propagates formats, enables upstream streams, and programs optional SoC gasket blocks.

## Important APIs, Types, and Functions
`struct mxc_isi_crossbar` stores the subdevice, pads, input enable counters, and parent ISI pointer. `mxc_isi_crossbar_init()` creates one sink pad per hardware input port plus one memory sink and one source pad per ISI channel. `__mxc_isi_crossbar_set_routing()` validates routes with `V4L2_SUBDEV_ROUTING_NO_N_TO_1` and forbids memory input routes except to the first pipeline. `mxc_isi_crossbar_xlate_streams()` maps requested source-pad streams back to the connected sink pad and remote upstream subdev.

Stream handling is in `mxc_isi_crossbar_enable_streams()` and `mxc_isi_crossbar_disable_streams()`. Optional gasket setup is wrapped by `mxc_isi_crossbar_gasket_enable()` and `mxc_isi_crossbar_gasket_disable()`. Pad ops include media-bus code enumeration, get/set format, set routing, and stream enable/disable.

## Control Flow
Initialization constructs the subdev, marks it as a media mux with stream support, allocates pads and per-input counters, initializes media pads, and finalizes subdev state. The initial state creates a default 1:1 mapping from hardware input ports to pipeline outputs. Sink-pad format setting validates the bus code, clamps dimensions to ISI limits, stores the sink stream format, and propagates it to active source routes. Source-pad formats are read-only mirrors of their routed sink side.

When a downstream pipe enables streams on a crossbar source pad, the crossbar translates the source streams through active routes, finds the remote upstream pad, enables the gasket on the first user of that sink input, and calls `v4l2_subdev_enable_streams()` upstream. Disabling decrements the input enable count, disables upstream streams when it reaches zero, and then disables the gasket.

## State and Persistence
Runtime state is the V4L2 subdev active routing table and each `mxc_isi_input.enable_count`. Routing and formats are stored in V4L2 subdev state. There is no persistent storage. Gasket registers are programmed only while streams are enabled.

## Dependencies and Integration Points
The file depends on V4L2 subdev streams/routing APIs, media pad graph helpers, ISI bus format helpers, and optional gasket ops supplied by platform data. It integrates directly with upstream camera/CSI subdevices and downstream ISI pipe subdevices through immutable media links created by the core.

## Risks and Edge Cases
The enable count is per input, not per stream, with a TODO noting limited multiplexed stream tracking. Route validation forbids fan-in but callers must still avoid unsupported topologies. Gasket enable requires a single-entry frame descriptor from the upstream source; multi-entry descriptors fail. `mxc_isi_crossbar_disable_streams()` decrements without defensive underflow protection, so stream enable/disable pairing must be correct.

## Test Signals
Useful tests include default 1:1 routing, route changes while idle, rejection of memory input to nonzero pipelines, format propagation from sink to source streams, busy rejection while streaming, upstream stream enable/disable call ordering, gasket programming for CSI-2 frame descriptors, and reference-count behavior when multiple consumers use the same input.
