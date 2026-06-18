# subset-b-004159 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-dvp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-dvp.c

Purpose: implements the DVP/parallel side of the Rockchip CIF capture driver. It defines DVP input/output format tables, SoC-specific register maps for PX30 VIP and RK3568 VICAP, optional RK3568 GRF setup, the DVP register accessors, stream start/stop programming, frame-end IRQ handling, crop programming, and registration of DVP media/video entities.

Important APIs/types/functions: exports `rkcif_px30_vip_dvp_match_data`, `rkcif_rk3568_vicap_dvp_match_data`, `rkcif_dvp_register()`, `rkcif_dvp_unregister()`, and `rkcif_dvp_isr()`. The `dvp_out_fmts`, `px30_dvp_in_fmts`, and `rk3568_dvp_in_fmts` tables map V4L2 fourcc/media-bus codes to CIF format bits, including YUV, Bayer RAW 8/10/12, RGB, grayscale, BT.1120, and interlaced variants. `rk3568_dvp_grf_setup()` programs `RK3568_GRF_VI_CON1` for clock delay and dual-edge datapath. `rkcif_dvp_queue_buffer()` writes Y/UV DMA addresses into ping-pong frame registers. `rkcif_dvp_start_streaming()` translates the active interface state and stream pixel format into `FOR`, stride, size, scaler bypass, IRQ enable, and capture-control registers.

Control flow: `rkcif_dvp_register()` creates one active DVP `rkcif_interface`, registers it as a V4L2 subdev, runs optional SoC setup, then registers one stream unless the match data says the hardware has four IDs. The shared vb2 stream layer calls `rkcif_dvp_start_streaming()` after initial buffers have been queued; DVP start reads the active source-pad format for the stream, resolves input/output formats, configures bus and memory format, clears interrupt/status registers, optionally bypasses the scaler, enables frame interrupts, and starts capture in ping-pong mode. The shared stream layer calls `rkcif_dvp_stop_streaming()` directly on timeout or indirectly through the IRQ stop path. `rkcif_dvp_isr()` reads interrupt/status/last-size registers, clears frame-end bits, honors `stream->stopping`, checks for bad frame height, resets capture on bad frames, then hands buffer rotation to `rkcif_stream_pingpong()`.

State and persistence: no disk persistence. Runtime state is held in `struct rkcif_interface` and `struct rkcif_stream`: active pad formats/crops in the V4L2 subdev state, `stream->pix`, `stream->buffers[]`, `frame_phase`, `stopping`, and the vb2 queue in `rkcif-stream.c`. Hardware state lives in memory-mapped DVP registers and, for RK3568, in GRF bits. `rkcif_dvp_stop_streaming()` clears capture, interrupts, interrupt status, frame status, and resets the stopping flag.

Dependencies/integration: depends on the shared CIF abstractions from `rkcif-common.h`, `rkcif-interface.c`, and `rkcif-stream.c`, V4L2 subdev/media-controller APIs, vb2 DMA buffers via the stream layer, Linux regmap for GRF setup, and register definitions from `rkcif-regs.h`. It is selected by `rkcif-dev.c` match data for `"rockchip,px30-vip"` and `"rockchip,rk3568-vicap"`.

Risks: DVP start returns `-EINVAL` if active source/output formats are missing, so media graph format negotiation must be complete before streaming. Register maps use `RKCIF_REGISTER_NOTSUPPORTED`; unsupported writes are silently ignored, which is intentional but can hide incomplete match-data coverage. Bad frame detection only checks last line against expected height and resets capture; it does not validate all dimensions or propagate a userspace error. Stop relies on the next frame-end IRQ through the shared stream wait path, with a forced stop fallback in `rkcif-stream.c`. RK3568 GRF setup depends on `rockchip,grf` and endpoint properties; missing GRF disables the setup silently.

Test signals: exercise DVP probe on PX30/RK3568-compatible DTs, media graph link creation, `v4l2-ctl --list-formats-ext` for DVP formats, format negotiation for YUV/Bayer/BT.1120, stream start/stop with one and two queued buffers, frame drop with an empty vb2 queue, crop changes through the interface subdev, and bad-frame/stop-timeout behavior through kernel logs and IRQ counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-dvp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-dvp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-dvp.h

Purpose: public internal header for the CIF DVP implementation. It exposes DVP match data and lifecycle/IRQ entry points to the platform driver.

Important APIs/types/functions: declares `rkcif_px30_vip_dvp_match_data`, `rkcif_rk3568_vicap_dvp_match_data`, `rkcif_dvp_register()`, `rkcif_dvp_unregister()`, and `rkcif_dvp_isr()`. It includes `rkcif-common.h`, so callers share the `struct rkcif_device` and `struct rkcif_dvp_match_data` definitions.

Control flow: `rkcif-dev.c` uses the match-data externs in SoC descriptors, calls `rkcif_dvp_register()` during probe/media entity setup, calls `rkcif_dvp_unregister()` during remove/error unwind, and dispatches the shared platform IRQ to `rkcif_dvp_isr()`.

State and persistence: this header has no state; it formalizes ownership boundaries between the platform glue and DVP module.

Dependencies/integration: local driver-only interface tied to `rkcif-capture-dvp.c` and `rkcif-dev.c`.

Risks: declarations must stay synchronized with the implementation and match data. Because match data is exported as objects rather than factory functions, any struct layout change in `rkcif-common.h` directly affects this interface.

Test signals: compile coverage for all supported compatibles and module builds; probe/unwind paths verify all declarations are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-dvp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-mipi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-mipi.c

Purpose: implements the MIPI capture side of the CIF/VICAP driver, primarily for RK3568. It defines MIPI output/input formats, per-ID register maps, MIPI CTRL0 encoding, per-stream DMA programming, stream start/stop, crop programming, IRQ handling, and registration of MIPI interface streams.

Important APIs/types/functions: exports `rkcif_rk3568_vicap_mipi_match_data`, `rkcif_mipi_register()`, `rkcif_mipi_unregister()`, and `rkcif_mipi_isr()`. `mipi_out_fmts` maps V4L2 packed YUV, RGB24/BGR24, Bayer RAW 8/10/12, and packed RAW10/12 formats to media-bus codes, MIPI CSI-2 data types, compact flags, and write-depth/type values. `mipi_in_fmts` enumerates accepted incoming media-bus codes. `rkcif_rk3568_mipi_ctrl0()` builds hardware CTRL0 fields for data type, compact packing, crop enable, write-to-DDR type, and capture enable. Register helpers add per-MIPI-block offsets and per-ID register offsets.

Control flow: `rkcif_mipi_register()` iterates match-data MIPI blocks, registers a V4L2 interface subdev for each block found in DT, then registers four stream video nodes (`ID0` through `ID3`) per active interface. The shared stream layer calls `rkcif_mipi_start_streaming()`, which resolves the active output format, computes CTRL0/CTRL1, enables frame0/frame1 interrupts for the stream ID, clears pending bits, writes virtual line widths for Y/UV frame slots, clears crop, writes size and CTRL0, and returns. `rkcif_mipi_isr()` loops all configured MIPI interfaces, clears interrupt status, checks each stream's frame0/frame1-end bits, stops on `stream->stopping`, or calls `rkcif_stream_pingpong()` for normal buffer rotation.

State and persistence: runtime state is stored in the shared `rkcif_interface` and `rkcif_stream` objects. Hardware state is per MIPI block and per stream ID; status and enable masks are read-modify-written because multiple IDs share interrupt registers. No persistent storage exists.

Dependencies/integration: relies on `media/mipi-csi2.h` for data-type constants, the common CIF register/match-data structs, V4L2/media-controller stream APIs through `rkcif-interface.c`, and vb2/ping-pong handling through `rkcif-stream.c`. `rkcif-dev.c` dispatches the shared IRQ and selects the RK3568 match data.

Risks: the implementation does not inspect active interface source media-bus format in `start_streaming()`, only the capture output format; link validation and interface format propagation must prevent mismatched sensor/MIPI/capture formats. Interrupt status clearing writes the raw status back and then per-stream code acts on the saved value, so incorrect hardware clear semantics would affect all streams. Multi-ID streams share global IRQ masks; races are limited by vb2 streaming serialization but format/routing misconfiguration can still enable unexpected IDs. `rkcif_mipi_register()` continues on interface registration errors and only fails if a stream registration fails, which can hide missing DT endpoints while allowing other interfaces.

Test signals: validate four virtual channels/IDs via media graph routing, per-ID `/dev/video` nodes, frame-end IRQs for both ping-pong slots, RAW packed/unpacked formats and bytesperline programming, crop offset programming, stop while frames are active, and simultaneous stream IDs sharing interrupt registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-mipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-mipi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-mipi.h

Purpose: public internal header for the CIF MIPI capture implementation.

Important APIs/types/functions: declares `rkcif_rk3568_vicap_mipi_match_data`, `rkcif_mipi_register()`, `rkcif_mipi_unregister()`, and `rkcif_mipi_isr()`. It imports `rkcif-common.h` for `struct rkcif_device` and match-data type definitions.

Control flow: consumed by `rkcif-dev.c` to attach RK3568 MIPI match data, register/unregister MIPI entities, and route the shared IRQ into the MIPI ISR.

State and persistence: no state; the header exposes module boundaries only.

Dependencies/integration: tightly coupled to `rkcif-capture-mipi.c` and platform match data.

Risks: any change to MIPI match-data shape or registration semantics requires this header and users to remain in sync.

Test signals: build/link coverage on RK3568 VICAP configs and probe/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-mipi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-common.h

Purpose: central data model for the Rockchip CIF driver. It defines constants, enum namespaces, format descriptors, stream/interface/device structures, and SoC match-data structures shared by DVP, MIPI, interface, stream, and platform modules.

Important APIs/types/functions: `RKCIF_DRIVER_NAME`, `RKCIF_CLK_MAX`, format/interface/id enums, `struct rkcif_buffer`, `struct rkcif_dummy_buffer`, `struct rkcif_input_fmt`, `struct rkcif_output_fmt`, `struct rkcif_remote`, `struct rkcif_stream`, `struct rkcif_interface`, `struct rkcif_mipi_match_data`, `struct rkcif_dvp_match_data`, `struct rkcif_match_data`, and `struct rkcif_device`. `struct rkcif_stream` contains ping-pong buffers, frame counters, stop waitqueue, vb2 queue, video device, and hardware hooks. `struct rkcif_interface` represents a V4L2 subdev bridge with sink/source pads, endpoint data, stream array, input formats, and optional crop callback.

Control flow: platform probe fills `struct rkcif_device` from match data, DVP/MIPI registration fills `struct rkcif_interface` and `struct rkcif_stream`, stream registration exposes video nodes, and the interface subdev propagates format/routing/crop state between remote sensors/receivers and stream nodes.

State and persistence: this header defines all persistent in-kernel runtime state for CIF. State includes media graph objects, async notifier links, clocks/reset/regmap/base address, active streams, queued buffers, dummy DMA storage, and match-data pointers. There is no filesystem persistence.

Dependencies/integration: includes Linux clocks/mutex/regmap and V4L2/media/vb2 headers plus `rkcif-regs.h`. It is the type contract among all files in this subset.

Risks: broad shared structs mean layout changes can ripple across all CIF modules. The `union` fields in format descriptors and interfaces require callers to respect whether a stream is DVP or MIPI. The `RKCIF_ID_MAX` and `RKCIF_IF_MAX` enum sizes drive fixed arrays; adding hardware instances requires careful array and routing updates.

Test signals: compile coverage across all CIF modules, probe of both PX30 and RK3568 match data, media graph enumeration, multi-stream MIPI routing, DVP single-stream behavior, and vb2 queue lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-dev.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-dev.c

Purpose: platform driver for the Rockchip CIF/VIP/VICAP device. It owns compatible matching, resource acquisition, media/v4l2 device registration, async sensor binding, top-level IRQ dispatch, runtime PM, and entity registration/unregistration.

Important APIs/types/functions: defines PX30 and RK3568 clock lists and `struct rkcif_match_data`, OF match table for `"rockchip,px30-vip"` and `"rockchip,rk3568-vicap"`, `rkcif_probe()`, `rkcif_remove()`, runtime PM callbacks, notifier callbacks, and shared `rkcif_isr()`. `rkcif_register()` calls DVP then MIPI registration; `rkcif_unregister()` unwinds in reverse.

Control flow: probe allocates `struct rkcif_device`, matches SoC data, maps registers, requests a shared IRQ, gets clocks, reset, optional GRF regmap, enables runtime PM, initializes media/v4l2 devices, initializes async notifier, registers DVP/MIPI entities, then registers the notifier. When a remote subdev binds, `rkcif_notifier_bound()` creates fwnode links to the interface sink pad; notifier completion registers subdev nodes. The IRQ handler calls DVP and MIPI ISRs and returns handled if either consumed the interrupt. Runtime resume enables clocks; runtime suspend resets the CIF block and disables clocks.

State and persistence: state lives in `struct rkcif_device`, including match data, clock/reset handles, base address, optional GRF, interface array, media device, v4l2 device, and notifier. Runtime PM state is kernel-managed; no disk persistence.

Dependencies/integration: integrates with platform resources, DT/fwnode graph, syscon GRF, reset controller, clk bulk API, runtime PM, V4L2 async notifier, media controller, DVP/MIPI modules, and shared stream/interface abstractions.

Risks: `devm_request_irq()` uses `IRQF_SHARED` and passes `dev` as context; both DVP and MIPI sub-ISRs must ignore unrelated interrupts. Runtime suspend performs a reset because it cannot reset on resume without disrupting IOMMU; this makes suspend/resume ordering important for active DMA users. If DVP/MIPI registration returns `-ENODEV`, the platform keeps probing, so DT endpoints determine which interfaces appear. Cleanup order must match registration because async notifier and media entities retain graph references.

Test signals: platform probe/remove on both compatibles, failure injection at media/v4l2/notifier/entity registration points, runtime PM suspend/resume under active and idle states, shared IRQ behavior when only DVP or MIPI is present, and async sensor link creation from DT endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-interface.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-interface.c

Purpose: V4L2 subdev abstraction for CIF input interfaces and crop units. It bridges a remote sensor or CSI receiver on a sink pad to one or more DMA stream video nodes on a source pad, handling media-bus format propagation, stream routing, crop state, and upstream stream enable/disable.

Important APIs/types/functions: exports `rkcif_interface_register()`, `rkcif_interface_unregister()`, and `rkcif_interface_find_input_fmt()`. Key callbacks are `rkcif_interface_set_fmt()`, `get/set_selection`, `set_routing`, `enable_streams`, `disable_streams`, and `init_state`. It uses `V4L2_SUBDEV_FL_STREAMS` and validates routes as one-to-one with source streams below `RKCIF_ID_MAX`.

Control flow: registration initializes the subdev, pads, default state, and device registration, then `rkcif_interface_add()` parses the DT endpoint for the interface index, validates DVP bus type, reads optional DVP clock delay, adds the remote endpoint to the async notifier, and marks the interface active. Format setting is sink-driven: source format always mirrors sink format and crop is reset to the full new size. Crop is only exposed on the source pad. Stream enable first applies crop to hardware through the interface callback, translates source stream masks to sink streams, then enables the upstream remote subdev stream. Disable translates and disables upstream streams.

State and persistence: active format/crop/routing state is in V4L2 subdev state. `struct rkcif_interface` stores endpoint parse data, remote async connection, status, stream array, input format table, and optional crop callback. No persistent storage.

Dependencies/integration: relies on media-controller pad links, V4L2 subdev state/routing helpers, fwnode endpoint parsing, V4L2 async notifier in `rkcif-dev.c`, and hardware crop callbacks from DVP/MIPI modules.

Risks: `media_pad_remote_pad_first()` in stream enable/disable assumes a connected remote pad; bad media graph setup can lead to null/invalid use. Crop is copied directly from userspace selection and only adjusted indirectly by users of the source format, so invalid crop dimensions could produce hardware programming mismatches unless bounded by V4L2 helpers/userspace discipline. DVP has one crop for all IDs and uses stream ID0, while MIPI applies crop per active route; route mistakes can program the wrong stream.

Test signals: subdev format propagation sink to source, crop get/set/default/bounds, stream routing with MIPI IDs, DVP crop shared behavior, async endpoint parsing for DVP and MIPI ports, and upstream sensor stream-on/off ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-interface.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-interface.h

Purpose: internal interface contract for the CIF input/crop subdev abstraction.

Important APIs/types/functions: declares `rkcif_interface_register()`, `rkcif_interface_unregister()`, and `rkcif_interface_find_input_fmt()`. The file comment documents the design: one sink pad connected to a remote DVP companion or MIPI CSI-2 receiver, one source pad connected to one or more DMA stream abstractions.

Control flow: DVP and MIPI modules call register/unregister around their stream setup; capture start paths indirectly use `rkcif_interface_find_input_fmt()` to validate/translate active media-bus codes.

State and persistence: no state in the header; state is in `struct rkcif_interface` from `rkcif-common.h`.

Dependencies/integration: connects `rkcif-interface.c` to DVP/MIPI and platform modules.

Risks: as a small internal header, the main risk is stale declarations or comments drifting from the media topology implemented in the C file.

Test signals: compile/link plus media graph inspection showing interface subdevs correctly inserted between remote source and stream video nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-regs.h

Purpose: register bit definitions and register index enums for the CIF DVP and MIPI capture driver.

Important APIs/types/functions: defines `RKCIF_REGISTER_NOTSUPPORTED`, coordinate/fetch helpers, DVP control/interrupt/status/format/scaler bits, RK3568 GRF offsets and write-enable helper, DVP register indices (`enum rkcif_dvp_register_index`), MIPI block register indices (`enum rkcif_mipi_register_index`), and per-stream MIPI ID register indices (`enum rkcif_mipi_id_register_index`).

Control flow: match-data tables in DVP/MIPI modules map these enum indices to SoC-specific offsets. Register helper functions validate an enum index, look up the offset, and skip unsupported registers.

State and persistence: header constants only. Hardware state is controlled by writes from DVP/MIPI modules.

Dependencies/integration: consumed by `rkcif-common.h`, `rkcif-capture-dvp.c`, and `rkcif-capture-mipi.c`. Uses Linux `BIT()`/`GENMASK()` style macros via included kernel headers in users.

Risks: wrong bit definitions or enum ordering directly misprograms hardware. The sentinel value must not collide with real register offsets. Some duplicated macro names such as `RKCIF_INTSTAT_*` refer to different hardware contexts and require careful local interpretation.

Test signals: hardware stream tests across supported SoCs, register dumps while streaming, IRQ enable/status behavior, and compile warnings for missing enum initializers in match-data tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-stream.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-stream.c

Purpose: shared DMA/video-node implementation for CIF DVP and MIPI streams. It owns vb2 queue operations, ping-pong buffer rotation, dummy-buffer fallback, V4L2 capture ioctls, media link validation, video device registration, and stream start/stop integration with the interface subdev.

Important APIs/types/functions: exports `rkcif_stream_pingpong()`, `rkcif_stream_register()`, `rkcif_stream_unregister()`, and `rkcif_stream_find_output_fmt()`. Internal helpers manage driver queue push/pop under a spinlock, complete buffers with sequence/timestamps, allocate/free dummy DMA storage, prepare vb2 DMA addresses including single-plane fallback for multi-component formats, and fill/clamp pixel formats.

Control flow: vb2 start resets frame counters, starts the media pipeline, resumes runtime PM, pops two initial buffers or installs a dummy second buffer, calls the hardware-specific `start_streaming` hook, then enables the corresponding source stream on the interface subdev. Frame IRQs from DVP/MIPI call `rkcif_stream_pingpong()`, which completes the just-finished non-dummy buffer, pulls a new queued buffer or dummy, writes hardware addresses through `queue_buffer`, then flips `frame_phase`. vb2 stop disables the interface stream upstream, waits up to one second for the hardware-specific ISR stop path to clear `stopping`, forces `stop_streaming` on timeout, returns all buffers as error, drops runtime PM, and stops the media pipeline.

State and persistence: per-stream state includes `driver_queue`, `buffers[2]`, dummy DMA buffer, `frame_idx`, `frame_phase`, `stopping`, waitqueue, V4L2 pixel format, vb2 queue, video device, and media pipeline. No durable persistence. DMA addresses are derived from queued vb2 buffers and dummy allocation.

Dependencies/integration: requires vb2 DMA-contig, V4L2 ioctl/file ops, media controller links, runtime PM, and hardware callbacks installed by DVP/MIPI registration. The interface subdev performs upstream stream control.

Risks: dummy buffer sizing assumes all planes fit in `pix->num_planes * plane0.sizeimage`; this is safe for many formats but should be rechecked when adding asymmetric multi-plane formats. `rkcif_stream_start_streaming()` jumps to `err_runtime_put` if the hardware hook fails after dummy allocation, but dummy freeing happens only in `rkcif_stream_return_all_buffers()`, so error paths depend on that cleanup. Link validation checks width/height but not media-bus code, relying on stream format tables and interface negotiation. Stop waits for an IRQ; if no frame arrives, forced stop happens after timeout.

Test signals: vb2 queue setup/prepare for single-plane and multi-plane formats, start with one queued buffer and with two queued buffers, frame drop/dummy-buffer path, stream stop with and without a final frame IRQ, media link validation failures for size mismatch, and format enumeration/clamping at min/max dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-stream.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-stream.h

Purpose: internal header for the CIF DMA stream/video-node abstraction.

Important APIs/types/functions: declares `rkcif_stream_pingpong()`, `rkcif_stream_register()`, `rkcif_stream_unregister()`, and `rkcif_stream_find_output_fmt()`. The file comment describes each stream as a V4L2 capture device with a sink pad connected to an interface/crop subdev and a ping-pong DMA scheme.

Control flow: DVP/MIPI modules install callbacks and call `rkcif_stream_register()`; their ISRs call `rkcif_stream_pingpong()`; unregister paths call `rkcif_stream_unregister()`.

State and persistence: no state in the header; per-stream state is in `struct rkcif_stream`.

Dependencies/integration: bridges `rkcif-stream.c` to DVP/MIPI modules and shared common types.

Risks: exported behavior assumes hardware modules provide compatible callbacks for queueing, start, and stop. Header comments should stay aligned with the media graph design.

Test signals: compile/link and media graph validation with stream video nodes connected to interface source pads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/Kconfig

Purpose: Kconfig entry for building the Rockchip ISP1 V4L2 media driver.

Important APIs/types/functions: defines `CONFIG_VIDEO_ROCKCHIP_ISP1` as a tristate option named "Rockchip Image Signal Processing v1 Unit driver". It depends on V4L platform drivers, V4L2 device support, OF, and either Rockchip/i.MX architecture or `COMPILE_TEST`. It selects media controller, V4L2 subdev API, vb2 DMA-contig and vmalloc backends, V4L2 fwnode, generic MIPI D-PHY, and V4L2 ISP helpers.

Control flow: when enabled, the Makefile builds `rockchip-isp1.o`, which registers the platform driver in `rkisp1-dev.c`. The module name documented to users is `rockchip-isp1`.

State and persistence: build-time configuration only.

Dependencies/integration: integrates the driver into the kernel media platform menu and ensures required media/vb2/PHY infrastructure is selected.

Risks: missing selects/dependencies cause build failures or runtime missing symbols; overly broad selects can build unused infrastructure. The dependency includes `ARCH_MXC` because i.MX8MP uses this ISP block through the same driver.

Test signals: allmodconfig/allyesconfig, COMPILE_TEST on non-Rockchip architectures, module build, and boot probing on RK3399/PX30/i.MX8MP DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/Makefile

Purpose: build manifest for the `rockchip-isp1` composite kernel module.

Important APIs/types/functions: `rockchip-isp1-y` includes capture, common, CSI, platform device, ISP subdev, resizer, stats, and params objects. `rockchip-isp1-$(CONFIG_DEBUG_FS)` conditionally adds `rkisp1-debug.o`. `obj-$(CONFIG_VIDEO_ROCKCHIP_ISP1)` attaches the module to the Kconfig option.

Control flow: Kbuild links all listed objects into one module, so internal symbols declared in `rkisp1-common.h` can be shared without exporting to other modules.

State and persistence: build-time only.

Dependencies/integration: matches the Kconfig symbol and the driver’s internal source layout.

Risks: forgetting a new entity object here would build declarations but fail at link or omit runtime functionality. Debugfs code is intentionally conditional.

Test signals: module build with and without `CONFIG_DEBUG_FS`, link-time validation of all internal symbols, and `modinfo rockchip-isp1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-capture.c

Purpose: V4L2 capture implementation for RKISP1 mainpath and selfpath. It defines supported memory formats, configures the memory interface, manages vb2 buffers, handles frame-end IRQs, starts/stops capture pipelines, validates media links, and registers capture video devices.

Important APIs/types/functions: exports `rkisp1_cap_enum_mbus_codes()`, `rkisp1_capture_isr()`, `rkisp1_capture_devs_register()`, and `rkisp1_capture_devs_unregister()`. Key internal types are `rkisp1_capture_fmt_cfg`, `rkisp1_capture_ops`, and `rkisp1_capture_config`. Format tables `rkisp1_mp_fmts` and `rkisp1_sp_fmts` map V4L2 formats to MI write/output bits and resizer media-bus codes. Operations split MP/SP specifics for config, enable/disable, data path, and stopped checks.

Control flow: registration initializes each supported path (`rkisp1_path_count()` controls whether selfpath exists), sets default YUYV 800x600, initializes vb2/video/media entities, and registers `/dev/video*`. vb2 start serializes with `stream_lock`, starts the media pipeline, creates a dummy DMA buffer, resumes runtime PM, gets pipeline PM, calls `rkisp1_pipeline_stream_enable()`, and returns queued buffers on error. Pipeline enable first configures/enables MI capture, then starts the matching resizer, then starts ISP/source if no other path is already streaming. Frame-end IRQs are handled before ISP IRQs by the top-level driver; `rkisp1_capture_isr()` completes current buffers with the ISP frame sequence, rotates next buffers into hardware shadow registers, handles stop sequencing, and wakes the stop waitqueue when shadow registers show the path is stopped. Stop disables the pipeline in reverse, waits up to one second for IRQ-confirmed stop, returns buffers as error, releases PM, destroys dummy storage, and stops the media pipeline.

State and persistence: persistent runtime state is in `struct rkisp1_capture`: current/next queued buffers, dummy DMA buffer, queue spinlock, `is_streaming`, `is_stopping`, waitqueue, pixel format config, stride, and vb2/video node. Hardware state is in MI registers for sizes, strides, base addresses, offsets, format control, output alignment, data path, and interrupt masks. No disk persistence.

Dependencies/integration: depends on `rkisp1-common.h` for device, path, and feature flags; `rkisp1-regs.h` for MI register bits; vb2 DMA-contig; media-controller pipeline PM; runtime PM; resizer and ISP subdevs; and stats/params indirectly through ISP frame sequencing. It relies on `rkisp1-dev.c` dispatch ordering so buffers get the correct `frame_sequence` before the ISP ISR may advance it.

Risks: shadow-register timing is delicate: starting a second path intentionally avoids force-updating MI init to prevent dropping extra buffers. Stop relies on frame-end IRQ and shadow status, with forced stop after timeout. Format table order is significant for `rkisp1_cap_enum_mbus_codes()` because duplicate mbus entries must be grouped. Some byte/YC swap formats are only exposed when `MAIN_STRIDE` exists; adding formats must respect hardware swap limitations. Dummy buffer size is the max component size and is used for all planes when dropping frames; new formats should be checked. Link validation enforces source width/height/mbus matching, so misconfigured resizer formats fail at stream start.

Test signals: enumerate MP/SP formats by mbus code, test YUV packed/planar/semi-planar and Bayer RAW, stream MP only/SP only/both simultaneously, stress start/stop at high FPS, verify frame sequence alignment with frame-sync events, trigger buffer underrun to increment debug frame-drop counters, test timeout path by suppressing frame-end IRQ, validate stride behavior on MAIN_STRIDE and non-MAIN_STRIDE devices, and run media-ctl pipelines through link validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-common.c

Purpose: shared format and crop helpers for the RKISP1 driver.

Important APIs/types/functions: defines the `rkisp1_formats` media-bus table and exports `rkisp1_mbus_info_get_by_index()`, `rkisp1_mbus_info_get_by_code()`, `rkisp1_sd_adjust_crop_rect()`, `rkisp1_sd_adjust_crop()`, and `rkisp1_bls_swap_regs()`. The format table covers YUV source, Bayer sink/source RAW 8/10/12 with CSI-2 data type, bus width, and Bayer pattern, plus YUV sink formats with acquisition sequence bits.

Control flow: subdevs use index/code lookups for enumeration and validation; ISP/CSI/capture/resizer modules use returned metadata to choose acquisition mode, MIPI data type, Bayer pattern, output conversion, and media-bus compatibility. Crop helpers enforce RKISP1 minimum dimensions and map requested rectangles inside bounds.

State and persistence: static immutable format table only; helper functions mutate caller-provided crop/output arrays.

Dependencies/integration: depends on V4L2 media-bus constants, MIPI CSI-2 data types, V4L2 rect helpers, and register bit definitions from `rkisp1-regs.h`.

Risks: the format table is a single source of truth; omissions or wrong direction flags break enumeration and stream validation across multiple subdevs. `rkisp1_bls_swap_regs()` indexes a fixed pattern table and assumes a valid Bayer pattern enum from format metadata.

Test signals: format enumeration on CSI/ISP/resizer/capture, media pipelines using all Bayer patterns and YUV orders, crop boundary tests, and BLS register ordering tests when changing Bayer pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-common.h

Purpose: central header for RKISP1 types, feature flags, constants, inline register accessors, and internal function declarations.

Important APIs/types/functions: defines driver names, dimensions, IRQ lines, pad enums, stream IDs, Bayer patterns, feature bits and `rkisp1_has_feature()`, `struct rkisp1_info`, async sensor metadata, CSI/ISP/capture/stats/params/resizer/debug/device structs, `struct rkisp1_mbus_info`, `rkisp1_write()`, `rkisp1_read()`, format/crop helpers, params hooks, IRQ handlers, and entity registration prototypes. `struct rkisp1_device` aggregates platform resources, media/v4l2 devices, notifier, subdevs, video nodes, media pipeline, stream lock, debug counters, match info, IRQs, and IRQ enable state.

Control flow: every RKISP1 module includes this header. Platform probe fills `rkisp1_device` and `rkisp1_info`; entity modules register subdevices/video nodes; IRQ handlers and stream callbacks share the same device and per-entity state.

State and persistence: defines all long-lived in-kernel state for the driver: clocks, PM domains, gasket, active source, CSI source, ISP frame sequencing, capture current/next buffers, metadata queues, debug counters, pipeline lock, and IRQ state. No disk persistence.

Dependencies/integration: includes kernel clock/interrupt/mutex/config headers and V4L2/media/vb2 headers, plus `rkisp1-regs.h`. It is the internal ABI for objects linked into `rockchip-isp1.o`.

Risks: because this is a wide shared header, changes can affect all module boundaries. Feature flags must remain consistent with match data in `rkisp1-dev.c`; wrong flags enable unsupported register paths. State fields used from IRQ and process contexts require the locking discipline documented in each struct comment.

Test signals: full module compile, sparse/lockdep review for lock comments, probe on all match-data variants, runtime stream tests for devices with and without selfpath/MIPI/MAIN_STRIDE/DMA_34BIT, and debugfs counter sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-csi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-csi.c

Purpose: internal MIPI CSI-2 receiver subdev for RKISP1 variants with `RKISP1_FEATURE_MIPI_CSI2`. It links sensors to the CSI receiver, configures CSI/MIPI registers and D-PHY timing, forwards streaming to the source sensor, handles MIPI interrupts, and registers the CSI media entity.

Important APIs/types/functions: exports `rkisp1_csi_link_sensor()`, `rkisp1_csi_register()`, `rkisp1_csi_unregister()`, `rkisp1_csi_init()`, and `rkisp1_csi_cleanup()`, plus ISR `rkisp1_csi_isr()` declared in common. Key internals are `rkisp1_csi_config()`, `rkisp1_csi_start()`, `rkisp1_csi_stop()`, pad format ops, and `rkisp1_csi_s_stream()`.

Control flow: platform notifier binds a sensor and calls `rkisp1_csi_link_sensor()`, which requires a `V4L2_CID_PIXEL_RATE` control and creates a sensor-to-CSI link. During stream-on, the CSI subdev finds its unique remote source, retrieves async sensor metadata, validates CSI2 D-PHY bus type, gets active sink format, configures lane count/data type/interrupt masks, computes D-PHY timing from pixel rate, powers on the D-PHY, enables CSI output, waits briefly, and starts the sensor. Stream-off stops the sensor, disables/masks CSI interrupts, synchronizes the MIPI IRQ, clears status, disables output, and powers off the PHY.

State and persistence: `struct rkisp1_csi` stores D-PHY handle, `is_dphy_errctrl_disabled`, subdev/pads, source pointer, and parent device. Active pad formats live in subdev state. No persistent storage.

Dependencies/integration: uses generic PHY MIPI D-PHY APIs, V4L2 controls/fwnode/media links, `rkisp1_mbus_info` for data types and bus widths, and platform IRQ/PM state from `rkisp1-dev.c`. The CSI source pad links to the ISP sink in `rkisp1_create_links()`.

Risks: no pixel-rate control means sensor link fails; sensors must expose accurate `V4L2_CID_PIXEL_RATE`. DPHY error-control interrupts can remain asserted for a long time, so the ISR masks them until a clean frame-end; errors after masking are counted but may not interrupt until re-enabled. Lane count is limited to 1..4. Stream-off assumes `csi->source` was set by stream-on.

Test signals: sensor binding with pixel-rate control, CSI stream-on/off ordering, D-PHY lane/pixel-clock configuration, MIPI data type selection for RAW/YUV formats, injected DPHY/CSI errors and `mipi_error` counter behavior, and pad format propagation sink to source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-csi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-csi.h

Purpose: internal header for the RKISP1 CSI-2 receiver module.

Important APIs/types/functions: forward-declares CSI/device/sensor async structs and declares `rkisp1_csi_init()`, `rkisp1_csi_cleanup()`, `rkisp1_csi_register()`, `rkisp1_csi_unregister()`, and `rkisp1_csi_link_sensor()`.

Control flow: `rkisp1-dev.c` calls init/cleanup around PHY lifetime, register/unregister around media entity lifetime, and `rkisp1_csi_link_sensor()` from async notifier binding for port 0 sensors.

State and persistence: no state in the header; state is in `struct rkisp1_csi`.

Dependencies/integration: connects platform glue to `rkisp1-csi.c`.

Risks: CSI functionality is compiled into the module but should only be initialized/registered when match-data feature flags advertise MIPI CSI2.

Test signals: compile/link for MIPI-capable and non-MIPI variants, probe cleanup after CSI init failures, and sensor binding through port 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-csi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-debug.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-debug.c

Purpose: optional debugfs support for RKISP1. It exposes debug counters, sampled input status, and selected live/shadow register dumps when `CONFIG_DEBUG_FS` is enabled.

Important APIs/types/functions: exports `rkisp1_debug_init()` and `rkisp1_debug_cleanup()`. Internal `struct rkisp1_debug_register` describes register dumps, `rkisp1_debug_dump_regs()` reads registers only if runtime PM says the device is active, and show functions dump core, ISP, resizer, and MI mainpath registers. `rkisp1_debug_input_status_show()` samples ISP input flags 10,000 times with 1 us delay and reports VSYNC/HSYNC/data distribution.

Control flow: platform probe calls `rkisp1_debug_init()` after notifier/entity setup; remove calls cleanup. debugfs files are read on demand. Register dump reads call `pm_runtime_get_if_in_use()` and return `-ENODATA` if the device is suspended/inactive.

State and persistence: debug counters live in `struct rkisp1_debug` and are incremented by ISR/stream paths; debugfs directory dentries are stored for cleanup. No durable persistence and counters reset when driver reloads.

Dependencies/integration: depends on debugfs, seq_file, runtime PM, RKISP1 register definitions, and counters maintained by `rkisp1-isp.c`, `rkisp1-csi.c`, and `rkisp1-capture.c`.

Risks: debugfs reads intentionally avoid waking the device, so register dumps may be unavailable when idle. The input status sampler busy-waits for about 10 ms and should not be used as a high-frequency polling interface. Register lists must be kept up to date with hardware/register changes.

Test signals: with `CONFIG_DEBUG_FS`, verify directory creation/removal, counter increments under frame drops/errors/timeouts, register dumps while streaming, `-ENODATA` while inactive, and input status output during sensor activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-dev.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-dev.c

Purpose: base platform driver for RKISP1. It owns DT matching, SoC feature data, IRQ setup, clocks/PM domains/gasket resources, media and V4L2 device registration, entity registration/linking, async sensor notifier, runtime PM, top-level IRQ dispatch, and module registration.

Important APIs/types/functions: defines `struct rkisp1_isr_data`, notifier callbacks, runtime PM callbacks, `rkisp1_create_links()`, entity register/unregister helpers, top-level `rkisp1_isr()`, SoC info for PX30, RK3399, and i.MX8MP, clock/PM-domain init helpers, `rkisp1_probe()`, and `rkisp1_remove()`. Feature data controls MIPI CSI2, selfpath, dual crop, main stride, 34-bit DMA, BLS, and companding availability.

Control flow: probe allocates `rkisp1_device`, sets DMA mask based on `DMA_34BIT`, initializes `stream_lock`, maps registers, requests SoC-defined IRQs by name or index, initializes clocks and optional PM domains, gets i.MX8MP gasket regmap/id when needed, enables runtime PM, briefly resumes to read CIF ID, initializes media/v4l2 devices, initializes CSI PHY when supported, registers ISP/resizer/capture/stats/params/CSI entities, creates fixed media links, registers async sensor notifier, and initializes debugfs. The notifier scans DT endpoints, maps port 0 to CSI2 and port 1 to parallel/BT656, adds remote fwnodes, and on bind creates sensor-to-CSI or sensor-to-ISP links. Runtime suspend disables IRQ handling with a memory barrier, synchronizes IRQs, disables clocks, and selects sleep pinctrl; resume selects default pinctrl, enables clocks, and re-enables IRQ handling.

State and persistence: all runtime state is in `struct rkisp1_device`. The async notifier stores sensor endpoint metadata until cleanup. `irqs_enabled` gates shared IRQ handlers across suspend/resume. No filesystem persistence.

Dependencies/integration: platform/OF graph, V4L2 fwnode async notifier, media controller, pinctrl, runtime PM, PM domains, clk bulk, syscon regmap for i.MX8MP, CSI/ISP/resizer/capture/stats/params modules, and optional debugfs. It is the top-level object linked by the Makefile/Kconfig.

Risks: endpoint parsing is strict: port 0 requires MIPI CSI2 feature and port 1 requires PARALLEL or BT656. IRQ dispatch order matters; capture ISR runs before ISP ISR to preserve frame sequence. Shared IRQ lines require each ISR to return `IRQ_NONE` quickly when disabled or status is empty. Error unwind must mirror the multi-entity registration order. i.MX8MP optional `pclk` compatibility and gasket configuration add variant-specific complexity.

Test signals: probe/remove on PX30, RK3399, and i.MX8MP compatibles; DT endpoint variations for MIPI and parallel sensors; runtime suspend/resume with IRQ storms; failure injection for clocks, IRQs, media registration, CSI init, and notifier registration; media graph topology inspection; and streaming with all supported path counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-isp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-isp.c

Purpose: ISP processing subdev for RKISP1. It models the ISP as a media entity with video sink/source plus params/statistics pads, configures acquisition, ISP crop/output crop/image-stabilization crop, input mux, i.MX8MP gasket, clocks, ISP start/stop, pad format/selection behavior, frame-sync events, and ISP IRQ handling.

Important APIs/types/functions: exports `rkisp1_isp_register()`, `rkisp1_isp_unregister()`, and `rkisp1_isp_isr()`. Key internals include `rkisp1_config_isp()`, `rkisp1_config_path()`, `rkisp1_config_ism()`, `rkisp1_config_cif()`, `rkisp1_isp_start()`, `rkisp1_isp_stop()`, pad enumeration/set-format/crop helpers, `rkisp1_isp_s_stream()`, and `rkisp1_isp_sof()`. i.MX8MP-specific helpers `rkisp1_gasket_enable()` and `rkisp1_gasket_disable()` configure media block control from upstream CSI-2 frame descriptors.

Control flow: subdev registration creates four pads and default state: Bayer sink, YUYV source, full crops, metadata params/stat pads. Format changes on the sink clamp dimensions, validate direction, normalize color metadata, and propagate to sink/source crops and source format. Source format supports Bayer passthrough, Bayer-to-YUV, and YUV passthrough, but rejects YUV-to-Bayer by falling back to the sink code. Stream-on finds the unique upstream source, determines bus type/flags from CSI or async sensor metadata, resets frame sequence/activity, locks active state, configures ISP acquisition/crop/path/ISM, enables clocks/gasket/ISP, post-configures params when output is YUV, then starts the upstream source. Stream-off stops upstream source, masks/synchronizes IRQs, clears status, disables ISP, waits for ISP off, resets MIPI/ISP blocks, and disables gasket on i.MX8MP.

State and persistence: `struct rkisp1_isp` holds active sink format metadata, frame sequence, frame-active flag, subdev, pads, and parent pointer. Active formats/crops are in V4L2 subdev state. Hardware registers hold acquisition, ISP control, crop, ISM, mux, clock, interrupt, and gasket state. No disk persistence.

Dependencies/integration: uses `rkisp1-common.c` format metadata and crop helpers, params pre/post/disable hooks, stats ISR, V4L2 event/subdev/media APIs, runtime register access, iopoll, regmap, and top-level source tracking in `rkisp1_device`. Capture paths start the ISP through `v4l2_subdev_call()` once pipeline PM is active.

Risks: upstream source uniqueness is mandatory; multiple enabled sensor links cause stream-on failure. Acquisition size uses `acq_mult` based on YUV/Bayer, so format metadata errors produce wrong sizes. Stop sequence must mask/synchronize both ISP and MI interrupts before clearing and disabling hardware. `readx_poll_timeout()` result is ignored, so a failed ISP-off wait is not surfaced. Frame-sync ordering is sensitive to IRQ latency; the code tracks delayed IRQs and increments debug counters.

Test signals: subdev format/crop negotiation for Bayer passthrough, Bayer-to-YUV, and YUV passthrough; frame-sync event subscription; stream-on/off through CSI and parallel sensors; params pre/post configuration ordering; stats ISR triggering on measurement bits; ISP error counters for size/data loss; i.MX8MP gasket data-type programming; and media link validation for params pad bypass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-isp.c -->
