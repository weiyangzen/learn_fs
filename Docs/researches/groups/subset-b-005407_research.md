# subset-b-005407 Research

Grouped research for AtomISP CSS runtime files. Each section preserves the original source path and is wrapped for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/src/ia_css_debug.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/src/ia_css_debug.c

Purpose: host-side diagnostics for the CSS/AtomISP runtime. It formats stream/frame enums, dumps FIFO/SP/pipeline/ISP parameter state, emits graphviz-style pipeline graphs, controls SP sleep/wake/debug DMA bits, and reads trace buffers/PC registers.

Important APIs/functions: `ia_css_debug_dtrace`, trace-level setters, FIFO dump helpers, `ia_css_debug_binary_print`, `ia_css_debug_frame_print`, `ia_css_debug_dump_sp_sw_debug_info`, `ia_css_debug_dump_isp_params`, `ia_css_debug_pipe_graph_dump_*`, config dump helpers, `ia_css_debug_dump_trace`, and `ia_css_debug_pc_dump`.

Control flow: most entry points are read-only dump routines that translate runtime structs or hardware/SP memory into debug output. Pipe graph generation is stateful: prologue initializes graph state, stage/raw-copy functions add nodes/edges, and epilogue emits deferred input-system/sensor nodes and resets temporary buffers. Trace dumping validates tracer headers, reads cyclic trace buffers, handles wraparound, then prints decoded entries.

State/persistence: global debug level `dbg_level` comes from the debug subsystem. This file owns static pipe-graph state (`pg_inst`, `dot_id_input_bin`, `ring_buffer`) and some static trace cursors/sample counters. It reads persistent SP DMEM and device registers but does not own them.

Dependencies/integration: tightly coupled to `ia_css_pipeline`, `ia_css_frame`, `ia_css_isp_param`, `sh_css_sp`, buffer queues, ISP kernel parameter dumpers, FIFO monitor, SP/ISP register accessors, and compile-time `SP_DEBUG`/`TRACE_ENABLE_*` feature flags.

Risks: many routines assume non-NULL objects and valid enum values via `assert`; malformed runtime state can produce truncated graph labels or invalid offsets. Debug paths read live hardware/SP memory without locking, so output can be inconsistent during active streaming. The DOT graph builder uses fixed-size static buffers and shared state, so concurrent callers can corrupt output.

Test signals: exercise stream/pipe/frame dumps with representative formats, verify DOT prologue/stage/epilogue ordering, compile with each `SP_DEBUG` mode, and use hardware/simulator traces to confirm wraparound and invalid-version handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/src/ia_css_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/event/interface/ia_css_event.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/event/interface/ia_css_event.h

Purpose: declares the software-event pack/unpack helpers used by host/SP event queues.

Important APIs/types: `ia_css_event_encode(u8 *in, u8 nr, uint32_t *out)` packs up to `MAX_NR_OF_PAYLOADS_PER_SW_EVENT` byte payloads into one 32-bit event; `ia_css_event_decode(u32 event, uint8_t *payload)` unpacks a raw event word into a four-byte payload. It depends on `type_support.h` and `sw_event_global.h`.

Control flow and state: the header is stateless and only defines the ABI. Callers allocate payload storage and pass the resulting event words to queue/eventq code.

Integration points: `runtime/event/src/event.c` implements the declarations; `runtime/eventq/src/eventq.c` uses them around `ia_css_queue_enqueue`/`dequeue`; higher layers such as pipeline/bufq send SP software events.

Risks: the API exposes raw pointers and does not express buffer length for `payload`; correctness relies on callers providing at least four bytes and valid `nr`.

Test signals: compile inclusion from both event and eventq paths, encode/decode four-byte round trips, invalid `nr` assertion/return behavior, and event-specific decode cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/event/interface/ia_css_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/event/src/event.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/event/src/event.c

Purpose: implements compact software-event encoding and host-side decoding for events exchanged with SP firmware.

Important functions: `ia_css_event_encode` divides 32 bits evenly across `nr` payload bytes, shifts existing output, and ORs each byte. `ia_css_event_decode` fills `payload[0..3]` from the event word, with special byte placement for `SH_CSS_SP_EVENT_PORT_EOF`, accelerator completion, timer, frame-tagged, firmware warning, and firmware assert events.

Control flow: encode initializes `*out` to zero, computes `nr_of_bits = 32 / nr`, and packs inputs in order. Decode starts with a common little-byte layout and then patches payload byte 3 for event classes that carry an extra high-byte field.

State/persistence: no owned state. It emits debug trace on decode and uses assertions to check expected zeroed payload bytes before writing.

Dependencies/integration: includes CSS/SP/debug headers and feeds `eventq.c`; event IDs come from `sw_event_global.h` and SP definitions.

Risks: `ia_css_event_encode` asserts validity before calculating but still computes only after assert; production builds must preserve the returned `false` path for invalid `nr`. Decode assumes caller zeroes payload bytes 1-3, which is not enforced by the type signature.

Test signals: encode with `nr` 1, 2, 4; decode all special event IDs; verify eventq receive provides a zeroed four-byte buffer or tolerates assertions in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/event/src/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/eventq/interface/ia_css_eventq.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/eventq/interface/ia_css_eventq.h

Purpose: public interface for sending host-to-SP software events and receiving SP-to-host event payloads through the generic CSS queue abstraction.

Important APIs: `ia_css_eventq_recv(ia_css_queue_t *eventq_handle, uint8_t *payload)` dequeues and decodes an event. `ia_css_eventq_send(ia_css_queue_t *eventq_handle, u8 evt_id, u8 evt_payload_0, u8 evt_payload_1, uint8_t evt_payload_2)` packs and enqueues an event, blocking until the queue is not full.

Control flow/state: the header is stateless; the queue handle carries all local/remote queue state.

Dependencies/integration: depends on `ia_css_queue.h`, with implementation in `eventq.c` and event packing from `ia_css_event.h`.

Risks: the send contract says blocking; users must avoid calling it from atomic contexts if the implementation busy-waits. Payload storage length is not encoded in the receive signature.

Test signals: local and remote queue send/receive, full queue retry behavior, empty receive returning `-ENODATA`, and invalid handle returning `-EINVAL` through queue APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/eventq/interface/ia_css_eventq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/eventq/src/eventq.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/eventq/src/eventq.c

Purpose: adapts the generic queue API to CSS event semantics.

Important functions: `ia_css_eventq_recv` dequeues a `u32` event word and decodes it into payload bytes when dequeue succeeds. `ia_css_eventq_send` fills a four-byte temporary payload, encodes it, then repeatedly calls `ia_css_queue_enqueue` until it succeeds or fails for a reason other than `-ENOBUFS`.

Control flow: receive is single-shot and propagates queue errors. Send is a busy-wait loop with `udelay(1)` for full queues, preserving `-EINVAL` or other queue errors.

State/persistence: no persistent state beyond the passed queue; all event words are transient queue items.

Dependencies/integration: depends on `ia_css_queue`, `ia_css_event`, and low-level delay support from platform headers. Used by host/SP control paths that signal pipeline and buffer events.

Risks: infinite wait is possible if the SP never drains a full queue. There is no cancellation/timeout and no explicit validation of `eventq_handle` before queue calls. Busy-waiting can be inappropriate under locks.

Test signals: enqueue-dequeue round trip, forced full queue until consumer drains, invalid queue handle, empty queue receive, and special event decode payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/eventq/src/eventq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/interface/ia_css_frame.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/interface/ia_css_frame.h

Purpose: declares host-side frame-info and frame-buffer helpers for CSS image buffers.

Important APIs: frame-info setters (`ia_css_frame_info_set_width`, `set_format`, `init`, `is_same_resolution`, `check_info`), plane initialization (`ia_css_frame_init_planes`), allocation/free helpers (`ia_css_frame_free_multiple`, `ia_css_frame_allocate_with_buffer_size`), type comparison, DMA port derivation (`ia_css_dma_configure_from_info`), and padded-width calculation.

Control flow/state: the header defines no state; callers pass `ia_css_frame`/`ia_css_frame_info` structs from public CSS types. Functions mutate those structs and may allocate backing memory in the implementation.

Dependencies/integration: depends on `ia_css_types.h`, frame format/public definitions, and `dma.h`. It is consumed by pipeline stage allocation, debug dumping, and DMA setup.

Risks: many functions assume valid pointers or valid format enums in implementation. Width padding must match ISP/HMM memory layout or DMA stride bugs follow.

Test signals: frame-info init across RAW/YUV/NV/RGB formats, invalid zero resolution, DMA config stride/elements for packed RAW and NV12_16, and cleanup of multiple partially allocated frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/interface/ia_css_frame.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/interface/ia_css_frame_comm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/interface/ia_css_frame_comm.h

Purpose: defines the compact frame structures shared with SP-side code.

Important types: SP plane structs for raw/binary/YUV/NV/RGB/six-plane layouts, `ia_css_sp_resolution`, `ia_css_frame_sp_info`, `ia_css_buffer_sp`, and `ia_css_frame_sp`. Conversion APIs map host `ia_css_frame_info` and `ia_css_resolution` to the SP representations.

Control flow/state: no owned state; the structs are ABI payloads that carry offsets, padded widths, format, raw depth/order, and buffer source metadata for SP queues or xmem addresses.

Dependencies/integration: includes buffer queue communication definitions and `system_local.h` for `ia_css_ptr`. `frame.c` implements the conversion functions; SP pipeline setup and buffer queue code consume the structures.

Risks: fields are narrowed to `u16`/`u8`, so callers must avoid silently truncating large dimensions or enum values. Struct layout is a cross-processor contract and should not be changed without SP firmware compatibility checks.

Test signals: host-to-SP conversion for max supported dimensions, raw metadata propagation, queue-id vs xmem buffer source selection, and ABI size/layout checks when compiler packing changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/interface/ia_css_frame_comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/src/frame.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/src/frame.c

Purpose: implements CSS frame layout, HMM allocation, padding, and DMA-port derivation.

Important functions: `ia_css_frame_allocate_from_info`, `ia_css_frame_allocate`, `ia_css_frame_free`, `ia_css_frame_init_planes`, `ia_css_frame_pad_width`, frame-info setters, `ia_css_frame_allocate_with_buffer_size`, `ia_css_frame_is_same_type`, `ia_css_dma_configure_from_info`, host-to-SP conversion helpers, and `ia_css_frame_init_from_info`.

Control flow: allocation creates a zeroed frame, initializes plane offsets/strides based on format, then allocates `data_bytes` through `hmm_alloc`. Plane initialization dispatches by frame format to single-plane, raw-packed, NV, YUV, RGB, six-plane, or binary helpers. DMA config converts frame info into stride/elements/width after checking padded width.

State/persistence: frame structs own an HMM buffer address in `frame->data` and transient plane metadata. Defaults set invalid queue/buffer IDs until higher layers bind frames to queues.

Dependencies/integration: depends on kernel allocation (`kvmalloc`/`kvfree`), HMM memory, frame formats, ISP vector/DDR constants, AtomISP logging, and pipeline stage creation.

Risks: format handling is hand-maintained and mismatched padding can underallocate or mis-stride hardware buffers. Odd heights are rounded for single-plane allocation but not uniformly for all formats. `ia_css_frame_is_same_type` dereferences frame pointers before null checks on frame objects.

Test signals: allocation/free for every supported format, invalid MIPI format rejection, raw bit-depth stride math, NV12_TILEY rounding, DMA config invalid padded width, and fault injection of HMM allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/src/frame.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/ifmtr/interface/ia_css_ifmtr.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/ifmtr/interface/ia_css_ifmtr.h

Purpose: exposes host-side input-formatter configuration helpers.

Important APIs/state: `ia_css_ifmtr_lines_needed_for_bayer_order`, `ia_css_ifmtr_columns_needed_for_bayer_order`, and `ia_css_ifmtr_configure`. The header also exposes `ifmtr_set_if_blocking_mode_reset`, a global reset guard controlling whether formatter blocking mode is programmed.

Control flow: callers provide a stream config and optional binary. The implementation computes crop starts, formatter buffer layout, and pushes configs into SP state when a physical input formatter is needed.

Dependencies/integration: depends on stream public config and binary descriptors; implementation calls input formatter hardware APIs and `sh_css_sp_set_if_configs`.

Risks: exposing the reset flag allows external code to affect global hardware reset behavior. Configuration is sensitive to input format, two-pixels-per-clock, bayer order, continuous/copy mode, and left padding.

Test signals: bayer-order line/column correction, memory input mode no-op config index, sensor-port config selection, and reset flag behavior across consecutive streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/ifmtr/interface/ia_css_ifmtr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/ifmtr/src/ifmtr.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/ifmtr/src/ifmtr.c

Purpose: calculates and installs input formatter configuration for sensor/buffered sensor streams, handling crop, bayer-order correction, YUV/RGB/raw deinterleaving, two-PPC, and input-buffer layout.

Important functions/state: public bayer correction helpers and `ia_css_ifmtr_configure`; private `ifmtr_start_column`, `ifmtr_input_start_line`, and `ifmtr_set_if_blocking_mode`; global `ifmtr_set_if_blocking_mode_reset`.

Control flow: configuration derives cropped dimensions and input format from the binary or stream config, selects formatter index from MIPI port or memory mode, computes start line/column, left padding, vector counts, buffer widths, deinterleaving, offsets, and `input_formatter_cfg_t` for formatter A and optionally B. For real formatter configs it resets/programs blocking mode once and calls `sh_css_sp_set_if_configs`.

State/persistence: no per-stream heap state, but hardware/SP formatter config and the global reset guard persist beyond the call.

Dependencies/integration: uses ISP vector constants, input formatter hardware functions, stream/binary metadata, `sh_css_sp`, and input-buffer ISP definitions.

Risks: many format cases hand-tune vector math; unsupported or width-zero results return `-EINVAL`. Global blocking reset is noted as problematic when streams start sequentially. Two-PPC crop and left-padding math are high-risk for off-by-one Bayer/YUV alignment bugs.

Test signals: matrix of input formats, two-PPC on/off, copy vs normal binary, continuous vs offline, odd crop offsets, left padding `-1`, and verification of SP if-config contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/ifmtr/src/ifmtr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/inputfifo/interface/ia_css_inputfifo.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/inputfifo/interface/ia_css_inputfifo.h

Purpose: declares the host/simulator path that pushes synthetic input frames and lines into the streaming-to-MIPI input FIFO.

Important APIs: full-frame send (`ia_css_inputfifo_send_input_frame`), streaming lifecycle (`start_frame`, `send_line`, `send_embedded_line`, `end_frame`). Parameters include MIPI channel id, stream format, optional two-PPC, line data pointers, and widths.

Control flow/state: callers can either send a whole frame in one call or manually bracket lines between start/end. Implementation tracks per-channel streaming state in static channel administration.

Dependencies/integration: includes SP/ISP headers and `ia_css_stream_format.h`; implementation depends on event FIFO, input system format conversion, and streaming-to-MIPI token definitions.

Risks: `ch_id` indexes a fixed four-entry table in implementation without header-level bounds. Data is raw `unsigned short` words and must already match format-specific packing assumptions.

Test signals: whole-frame RAW/YUV/RGB sends, manual embedded-line insertion, invalid channel bounds, two-PPC odd widths, and token stream inspection in simulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/inputfifo/interface/ia_css_inputfifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/inputfifo/src/inputfifo.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/inputfifo/src/inputfifo.c

Purpose: implements streaming-to-MIPI token generation for simulated/manual input frames.

Important functions/state: static token helpers (`inputfifo_send_data_a/b`, `inputfifo_send_sol/eol/sof/eof`, `inputfifo_send_line2`, `inputfifo_send_frame`), format classification (`inputfifo_determine_type`), and public frame/line APIs. Static globals hold current channel/format and per-channel `inputfifo_instance` records for four virtual channels.

Control flow: format conversion uses `ia_css_isys_convert_stream_format_to_mipi_format`. Start emits channel/format and SOF tokens. Each line emits blanking, SOL, marker tokens, pixel tokens to A/B lanes according to two-PPC and RGB/YUV420 legacy rules, trailing blanking, and EOL. End emits marker tokens and EOF.

State/persistence: per-channel admin persists across manual start/send/end. `_sh_css_fifo_snd` busy-waits until the event FIFO can accept a token.

Dependencies/integration: event FIFO, SP/ISP/IRQ inline accessors, input system MIPI format conversion, HIVE streaming-to-MIPI token bit definitions, and CSS input mode simulation.

Risks: fixed channel array has no explicit bounds guard. Busy-waiting can hang if event FIFO stops accepting tokens. RGB/YUV legacy two-PPC packing assumes callers inserted data in exact expected order.

Test signals: token traces for RAW/YUV420/YUV420 legacy/RGB, odd line widths, embedded metadata lines, full-frame vs manual API equivalence, and FIFO-full retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/inputfifo/src/inputfifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/interface/ia_css_isp_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/interface/ia_css_isp_param.h

Purpose: declares memory descriptor helpers and lifecycle functions for ISP parameter blocks.

Important APIs: setters/getters for host/CSS/ISP segment descriptors, `ia_css_init_memory_interface`, `ia_css_isp_param_allocate_isp_parameters`, `destroy_isp_parameters`, `load_fw_params`, `copy_isp_mem_if_to_ddr`, and `enable_pipeline`.

Control flow/state: callers describe per-parameter-class/per-memory sizes and offsets, allocate host and DDR parameter storage, optionally map firmware offset tables, copy host parameter images to DDR, then toggle the mandatory DMEM disable bit to enable the pipeline.

Dependencies/integration: uses `ia_css_isp_param_types.h`, `ia_css_err.h`, HMM DDR memory, and pipeline binaries' memory-offset metadata.

Risks: pointer/size arrays are indexed by enums with minimal runtime validation. `enable_pipeline` assumes the first DMEM param word is a control/disable field by protocol.

Test signals: allocation with sparse and full memory initializers, cleanup after partial allocation failure, copy size mismatch returning `-EINVAL`, firmware-offset initialization, and pipeline enable bit clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/interface/ia_css_isp_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/interface/ia_css_isp_param_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/interface/ia_css_isp_param_types.h

Purpose: defines the shared data model for ISP parameter memory classes and segment descriptors.

Important types/macros: `IA_CSS_ISP_DMEM`, `IA_CSS_ISP_VMEM`, `IA_CSS_NUM_ISP_MEMORIES`, `enum ia_css_param_class` (`PARAM`, `CONFIG`, `STATE`), `ia_css_isp_parameter`, host/CSS/ISP segment matrices, `ia_css_isp_param_memory_offsets`, and `union ia_css_all_memory_offsets`.

Control flow/state: no executable flow; these structs persist in binary/pipeline memory-parameter state and encode address/size pairs for each class and memory.

Dependencies/integration: uses public CSS types, platform alignment, and system memory enums. `isp_param.c`, debug parameter dumps, and binary loading consume these definitions.

Risks: class/memory dimensions must remain synchronized with firmware-generated offset structures. `union ia_css_all_memory_offsets` assumes aligned pointer slots and firmware layout compatibility.

Test signals: compile-time size/layout checks, iteration over `IA_CSS_NUM_PARAM_CLASSES` and `IA_CSS_NUM_MEMORIES`, and firmware offset parsing for all classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/interface/ia_css_isp_param_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/src/isp_param.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/src/isp_param.c

Purpose: implements allocation, descriptor management, firmware-offset mapping, DDR copy, and pipeline-enable mutation for ISP parameters.

Important functions: descriptor setters/getters, `ia_css_init_memory_interface`, `ia_css_isp_param_allocate_isp_parameters`, `ia_css_isp_param_destroy_isp_parameters`, `ia_css_isp_param_load_fw_params`, `ia_css_isp_param_copy_isp_mem_if_to_ddr`, and `ia_css_isp_param_enable_pipeline`.

Control flow: allocation initializes every class/memory slot from optional ISP initializers, allocates zeroed host memory for any nonzero size, and allocates HMM DDR memory for non-`PARAM` classes. Cleanup frees both host and DDR addresses. Copy validates host and DDR sizes per memory, skips empty slots, and `hmm_store`s host bytes to DDR.

State/persistence: host pointers and HMM addresses persist in caller-owned segment structs until destroy. Firmware parameter offset pointers can either be null or point into a loaded firmware blob.

Dependencies/integration: HMM memory manager, kernel allocation, pipeline/binary parameter metadata, and ISP memory enum constants.

Risks: no bounds validation for enum indices. `ia_css_isp_param_enable_pipeline` writes through a char buffer cast to `uint32_t *` and assumes alignment/protocol. Partial allocation cleanup must be preserved to avoid HMM leaks.

Test signals: allocation failure injection, idempotent destroy, non-parameter class DDR allocation, copy mismatch error, and pipeline-enable mutation on empty and non-empty DMEM params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isp_param/src/isp_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/interface/ia_css_isys.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/interface/ia_css_isys.h

Purpose: central public interface for CSS input-system initialization, RX configuration/IRQ handling, format conversion, virtual stream construction, and ISYS resource managers.

Important APIs/types: `ia_css_isys_init/uninit`, port conversion, CSI RX stream register/unregister, compressed/stream format conversion, alignment calculation, RX interrupt/configure functions, virtual stream create/destroy/calculate_cfg, and resource-manager init/acquire/release APIs for CSI RX LUTs, IBUF, DMA channels, and stream2mmio SIDs.

Control flow/state: callers initialize ISYS once, create/calculate streams, register them with CSI RX tracking, configure RX/virtual input-system blocks, then destroy streams and uninit resources.

Dependencies/integration: wraps `input_system.h`, stream/input port formats, `system_global.h`, and `ia_css_isys_comm.h`. Implemented across `isys_init.c`, `rx.c`, `virtual_isys.c`, and resource-manager files.

Risks: broad API exposes low-level resource acquisition and requires strict acquire/release pairing. Many implementation paths rely on assertions and static global resource tables.

Test signals: ISP2400 vs ISP2401 init, resource exhaustion/release, all MIPI format mappings, compression mappings, RX IRQ translation/clear, and virtual stream metadata paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/interface/ia_css_isys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/interface/ia_css_isys_comm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/interface/ia_css_isys_comm.h

Purpose: shared communication definitions for virtual input-system stream handles/configs and stream IDs.

Important types/macros: `SH_CSS_NODES_PER_THREAD`, `SH_CSS_MAX_ISYS_CHANNEL_NODES`, `ia_css_isys_stream_h`, `ia_css_isys_stream_cfg_t`, `ia_css_isys_error_t`, and inline `ia_css_isys_generate_stream_id(sp_thread_id, stream_id)`.

Control flow/state: no owned state. The stream ID formula maps SP thread plus per-channel stream id into a flat CSI RX tracking bit index.

Dependencies/integration: relies on `input_system.h`, `input_system_global.h`, platform inline support, and `IA_CSS_STREAM_MAX_ISYS_STREAM_PER_CH`. `csi_rx_rmgr.c` validates IDs against `SH_CSS_MAX_ISYS_CHANNEL_NODES`.

Risks: stream ID generation has no bounds check; callers must ensure both components fit the maximum node count. The comment notes handles are concrete structs because SP must interpret them, making layout an ABI concern.

Test signals: stream ID uniqueness across threads/channels, maximum boundary validation in register/unregister, and ABI build checks for virtual stream structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/interface/ia_css_isys_comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/csi_rx_rmgr.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/csi_rx_rmgr.c

Purpose: manages CSI RX backend LUT entries and tracks active virtual streams per MIPI port.

Important functions/state: static `isys_csi_rx_rsrc[N_CSI_RX_BACKEND_ID]`; init/uninit clear it. `ia_css_isys_csi_rx_lut_rmgr_acquire/release` allocates long/short packet LUT slots using a bitmap and counters. `ia_css_isys_csi_rx_register_stream/unregister_stream` set/clear bits in `sh_css_sp_group.pipe_io_status`.

Control flow: LUT acquire checks backend, packet type, and capacity, then finds the first free bit, fills either long or short entry, and increments active counters. Release clears matching bits and counters if the entry is valid and active.

State/persistence: backend resource tables and SP pipeline I/O status persist globally; no locking is present.

Dependencies/integration: bit operations, `ia_css_pipeline_get_pipe_io_status`, `sh_css_internal` limits, and CSI RX hardware constants.

Risks: resource manager is not thread-safe. The release assertion for packet type uses `||` semantics and is weaker than intended. Long and short packets share one active bitmap indexed from zero, so correctness depends on hardware LUT ranges and counters.

Test signals: allocate to capacity for long and short entries, release/reacquire reuse, invalid duplicate stream register/unregister, and concurrent stream setup serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/csi_rx_rmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/csi_rx_rmgr.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/csi_rx_rmgr.h

Purpose: private state definition for the CSI RX resource manager.

Important type: `isys_csi_rx_rsrc_t` stores `active_table`, total `num_active`, and separate `num_long_packets`/`num_short_packets` counters.

Control flow/state: no functions; `csi_rx_rmgr.c` owns a per-backend array of this struct. `active_table` is a bitset used to allocate LUT entries.

Dependencies/integration: depends on integer types made available by included compile context; consumed only by the CSI RX manager implementation.

Risks: the `u32` bitmap limits directly encode maximum LUT entries. If hardware exposes more than 32 entries or long/short tables should have disjoint spaces, the struct needs redesign.

Test signals: build-time compatibility with `N_LONG_PACKET_LUT_ENTRIES`/`N_SHORT_PACKET_LUT_ENTRIES`, counter consistency after allocate/release, and zeroed init state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/csi_rx_rmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/ibuf_ctrl_rmgr.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/ibuf_ctrl_rmgr.c

Purpose: fixed-size allocator for input-buffer controller scratch space.

Important functions/state: static `ibuf_rsrc`; `ia_css_isys_ibuf_rmgr_init/uninit` reset it and set `free_size` to 64 KiB. `ia_css_isys_ibuf_rmgr_acquire` aligns requested size to 8 bytes, reuses inactive handles large enough for the request, or allocates a new handle from the monotonic free region. `release` marks a handle inactive by start address.

Control flow: acquire first searches previously allocated handles, then grows the allocation table if capacity and free space remain. It returns the handle start address through the caller pointer.

State/persistence: allocated handle records persist after release for reuse; free region is monotonic and not compacted.

Dependencies/integration: used by `virtual_isys.c` channel creation to reserve IBUF storage.

Risks: no locking, no bounds validation beyond assertions, and no true free-space reclamation except reuse of whole handles. Fragmentation can cause failure even after releases if a larger size is needed.

Test signals: alignment rounding, exact reuse of released handles, exhaustion by handle count and byte size, release of unknown address, and init/uninit reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/ibuf_ctrl_rmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/ibuf_ctrl_rmgr.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/ibuf_ctrl_rmgr.h

Purpose: private data model and limits for the IBUF resource manager.

Important definitions: `MAX_IBUF_HANDLES` 24, `MAX_INPUT_BUFFER_SIZE` 64 KiB, `IBUF_ALIGN` 8, `ibuf_handle_t` with start/size/active, and `ibuf_rsrc_t` with free-region counters and handle array.

Control flow/state: header has no logic; `ibuf_ctrl_rmgr.c` mutates the single global instance.

Dependencies/integration: start addresses are offsets into input-buffer controller memory used by virtual ISYS channel configs.

Risks: static limits are hardware/protocol assumptions. The type has no owner/stream metadata, so double-release or wrong-address release cannot be reported except by no-op behavior.

Test signals: capacity boundary tests, zeroed init state, handle reuse expectations, and compatibility with maximum calculated virtual ISYS IBUF allocation size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/ibuf_ctrl_rmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_dma_rmgr.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_dma_rmgr.c

Purpose: allocates ISYS2401 DMA channels per DMA device.

Important functions/state: static `isys_dma_rsrc[N_ISYS2401_DMA_ID]`; init/uninit clear resource state; acquire finds the first inactive channel bit below the device's channel count and returns it; release clears an active channel bit and decrements the counter.

Control flow: acquire reads `N_ISYS2401_DMA_CHANNEL_PROCS[dma_id]`, checks `num_active`, iterates channel IDs, and marks the first free bit. Release validates channel range and active count before clearing.

State/persistence: per-DMA bitmap/counter state persists globally until uninit. No synchronization is provided.

Dependencies/integration: used by virtual ISYS channel creation to attach IBUF-to-VMEM/DDR transfer channels.

Risks: init/uninit call `memset(&isys_dma_rsrc, 0, sizeof(isys_dma_rsrc_t))`, which only clears one element rather than the whole array; if multiple DMA IDs exist, stale state can remain. Acquire iterates to `N_ISYS2401_DMA_CHANNEL` rather than `max_dma_channel` but guards by `num_active`.

Test signals: multi-DMA init reset, capacity exhaustion per DMA ID, release/reacquire, invalid DMA/channel assertions, and concurrent setup serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_dma_rmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_dma_rmgr.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_dma_rmgr.h

Purpose: private state definition for ISYS DMA channel allocation.

Important type: `isys_dma_rsrc_t` contains a `u32 active_table` bitmap and `u16 num_active` counter.

Control flow/state: no functions; `isys_dma_rmgr.c` owns an array indexed by DMA ID.

Dependencies/integration: channel count comes from ISYS2401 DMA constants, with channels represented as bit positions in `active_table`.

Risks: bitmap width caps channels at 32. State has no owner metadata, making leak/double release detection difficult.

Test signals: bitmap/counter invariants after allocate/release, max-channel compatibility, and reset coverage for every DMA ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_dma_rmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_init.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_init.c

Purpose: initializes and uninitializes the CSS input system for ISP2400 and ISP2401 variants.

Important functions: private `ia_css_isys_2400_init`, private `ia_css_isys_2401_init`, public `ia_css_isys_init`, and `ia_css_isys_uninit`.

Control flow: ISP2400 path resets input-system configuration, configures three CSI xmem channels with hard-coded memory/acquisition region sizes and targets, then commits. ISP2401 path initializes CSI RX LUT, IBUF, DMA, and stream2mmio resource managers, sets DMA0 max burst size to non-burst transactions, and enables ISYS IRQ status blocks. Public init selects by `IS_ISP2401`; uninit tears down ISP2401 resource managers.

State/persistence: hardware input-system configuration and resource-manager globals persist after init until uninit or reset.

Dependencies/integration: `input_system.h`, ISYS public APIs, `isys_dma_public.h`, and `isys_irq.h`.

Risks: ISP2400 configuration is hard-coded and must match hardware topology. ISP2401 init has no rollback if a later step fails, though it currently returns no-error after side effects.

Test signals: ISP2400 configuration failure propagation, ISP2401 resource managers reset, IRQ status enable effects, and repeated init/uninit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_stream2mmio_rmgr.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_stream2mmio_rmgr.c

Purpose: allocates stream2mmio stream IDs per stream2mmio block.

Important functions/state: static `isys_stream2mmio_rsrc[N_STREAM2MMIO_ID]`; init/uninit clear all entries; acquire uses `N_STREAM2MMIO_SID_PROCS[stream2mmio]` and a bitmap to return the first free SID; release clears an active SID.

Control flow: acquire validates block and output pointer, checks active count, scans from `STREAM2MMIO_SID0_ID` to max SID, sets the bit and counter. Release validates range and active bit before clearing.

State/persistence: global per-block bitmap/counter state persists until uninit; no locking.

Dependencies/integration: `virtual_isys.c` allocates one SID per data/metadata channel and releases it on stream destroy.

Risks: caller must pair acquire/release exactly. No owner tracking or synchronization. Bitmap width assumes SID count fits in 32 bits.

Test signals: per-block exhaustion, release/reacquire reuse, invalid SID release no-op, init/uninit clearing every stream2mmio ID, and multi-stream setup serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_stream2mmio_rmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_stream2mmio_rmgr.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_stream2mmio_rmgr.h

Purpose: private state model for stream2mmio SID allocation.

Important type: `isys_stream2mmio_rsrc_t` holds an active SID bitmap and active counter.

Control flow/state: no executable logic; implementation maintains one instance per stream2mmio block.

Dependencies/integration: tied to stream2mmio hardware constants and virtual ISYS channel descriptors.

Risks: no owner metadata and fixed bitmap width. Any change in hardware SID range must be reflected in the implementation and tests.

Test signals: active-table/counter invariants, maximum SID boundary, and reset state after init/uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_stream2mmio_rmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/rx.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/rx.c

Purpose: configures CSS receiver hardware, maps MIPI/AtomISP formats, translates/clears RX interrupts, and calculates input-system alignment/compression settings.

Important functions: `ia_css_isys_rx_enable_all_interrupts`, port conversion, IRQ get/clear/translate helpers, format mapping for ISP2400/2401, `ia_css_isys_convert_stream_format_to_mipi_format`, compression conversion, `ia_css_csi2_calculate_input_system_alignment`, `ia_css_isys_rx_configure`, and `ia_css_isys_rx_disable`.

Control flow: IRQ functions read receiver status registers and map hardware bits to `IA_CSS_RX_IRQ_INFO_*`. Format conversion selects compressed raw custom types or platform-specific MIPI constants. RX configure disables the selected port, writes timeout/count registers and GPREG routing, optionally updates global two-PPC registers if no port was already enabled, then re-enables the port.

State/persistence: writes receiver port/global registers and input-system GPREGs. No owned heap state.

Dependencies/integration: inline `input_system.h` receiver accessors, CSS IRQ enable, stream formats, compression structs, and `sh_css_internal` flags.

Risks: comments identify multi-stream hazards around shared two-PPC and GPREG mux/multicast programming. `ia_css_isys_rx_clear_irq_info` reads/writes the IRQ enable register while named as clearing status, requiring hardware-specific validation.

Test signals: IRQ bit translation for every bit, all supported input format mappings on ISP2400/2401, compression mapping invalid cases, lane table per RX mode/port, buffered vs non-buffered GPREG routing, and multi-stream receiver configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/virtual_isys.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/virtual_isys.c

Purpose: builds virtual ISP2401 input-system stream handles and calculates hardware configs for CSI/pixelgen input ports, stream2mmio, IBUF controller, DMA, and metadata channels.

Important functions/state: public `ia_css_isys_stream_create`, `destroy`, and `calculate_cfg`; private resource acquire/release wrappers; channel/input-port creation/destruction; config calculators for PRBS, CSI frontend/backend, stream2mmio, IBUF, DMA, DMA ports; `calculate_stride`; and packet-type classification.

Control flow: stream creation zeroes the handle, sets metadata/id/linkage, allocates input-port resources, allocates main channel resources, then optionally allocates metadata channel. Failures unwind prior allocations. Config calculation fills channel config, optional metadata config, and input-port config, then marks stream/config valid.

State/persistence: stream handles contain allocated resource IDs and buffer addresses; global resource managers own allocation tables. Calculated configs are caller-owned and later programmed into input-system hardware.

Dependencies/integration: ISYS resource managers, CSI RX constants, input-system virtual stream structs, ISP vector/DDRx constants, and debug tracing.

Risks: broad manual unwind logic must remain exact to avoid leaked SIDs/IBUF/DMA/LUT entries. Metadata handling shares input-port/backend resources and changes stores-per-frame. Alignment/stride math must agree with `frame.c`/DMA expectations.

Test signals: create/destroy with sensor, PRBS, metadata on/off, resource exhaustion at each allocation step, offline vs online IBUF/DMA config, raw-packed destination stride, compression/custom data type backend config, and valid flags after calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/virtual_isys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/virtual_isys.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/virtual_isys.h

Purpose: private constants for stream2mmio command tokens used by virtual ISYS configuration.

Important definitions: `_STREAM2MMIO_CMD_TOKEN_STORE_PACKETS` and `_STREAM2MMIO_CMD_TOKEN_SYNC_FRAME`.

Control flow/state: no logic or state. `virtual_isys.c` writes these constants into `ibuf_ctrl_cfg.stream2mmio_cfg` as store and sync commands.

Dependencies/integration: tied to stream2mmio hardware command semantics and IBUF controller config.

Risks: the numeric token values are hardware/firmware ABI. Wrong values would desynchronize frame sync or packet storage.

Test signals: config calculation checks that sync/store fields match expected token values and hardware tests confirm frame synchronization and packet capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/virtual_isys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/interface/ia_css_pipeline.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/interface/ia_css_pipeline.h

Purpose: declares the host-side pipeline/stage model for executing ISP binaries, firmware, and SP functions.

Important types/APIs: `ia_css_pipeline_stage`, `ia_css_pipeline`, `DEFAULT_PIPELINE`, `ia_css_pipeline_stage_desc`, lifecycle (`init`, `create`, `destroy`, `clean`), start/stop/status, stage add/finalize/get helpers, firmware/stage lookup, param usage query, SP thread map APIs, pipe I/O status accessor, and dump function.

Control flow/state: caller initializes the module, creates a pipeline with a unique `pipe_num`, maps it to an SP thread, appends stages from descriptors, finalizes stage numbers/ports, starts by sending SP events, and later requests stop/cleans.

Dependencies/integration: depends on `sh_css_internal`, public pipe types, frame structs, binary/firmware descriptors, and `ia_css_pipeline_common.h`.

Risks: pipeline and stage structs own frame pointers with allocation flags; lifetime rules are subtle. Static SP thread mapping is global and requires careful map/unmap.

Test signals: stage creation with binaries/firmware/SP funcs, automatic output/VF allocation, map/unmap boundaries, start/stop event emission, and cleanup freeing only owned frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/interface/ia_css_pipeline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/interface/ia_css_pipeline_common.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/interface/ia_css_pipeline_common.h

Purpose: shared pipeline stage function enumeration.

Important definitions: `enum ia_css_pipeline_stage_sp_func` values `RAW_COPY`, `BIN_COPY`, `ISYS_COPY`, and `NO_FUNC`; `IA_CSS_PIPELINE_NUM_STAGE_FUNCS` is 3, excluding `NO_FUNC`.

Control flow/state: no state. The enum lets stage descriptors and stage records distinguish SP-only copy/isys functions from normal ISP binary/firmware stages.

Dependencies/integration: consumed by pipeline creation, debug graph dump, and SP pipeline setup.

Risks: `IA_CSS_PIPELINE_NUM_STAGE_FUNCS` must stay synchronized with functional enum values. `NO_FUNC` is a sentinel and should not be counted as an executable SP function.

Test signals: switch/default handling for every enum, stage add validation for no binary/firmware/no func, and debug graph skipping SP funcs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/interface/ia_css_pipeline_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/src/pipeline.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/src/pipeline.c

Purpose: implements pipeline lifecycle, SP thread mapping, stage allocation/linking, start/stop events, output stage lookup, and port configuration.

Important functions/state: static `pipeline_num_to_sp_thread_map[20]` and `pipeline_sp_thread_list[SH_CSS_MAX_SP_THREADS]`; public init/create/map/destroy/start/request_stop/clean/add/finalize/get/status APIs; private stage destroy/create, defaults, zoom-stage selection, and in/out port config.

Control flow: module init resets maps. Stage addition validates descriptor, supplies previous output as input for eligible ISP stages, creates a stage, auto-allocates missing output/VF frames, and links it. Finalize assigns stage numbers, chooses zoom stage by pipe id, and encodes port sources/sinks for continuous/offline modes. Start initializes SP pipeline and enqueues start stream event; stop enqueues stop and uninitializes SP pipeline.

State/persistence: global pipe-to-thread maps persist. Pipelines own linked stage nodes and any frames marked allocated.

Dependencies/integration: HMM/frame allocation, buffer queue PSYS events, SP pipeline init/uninit/status, ISP params, debug tracing, and pipe/binary metadata.

Risks: mapping is unsynchronized and assert-heavy. `ia_css_pipeline_start` uses local `pipe_num = 0` instead of `pipeline->pipe_num`, which can surprise multi-pipe users. Firmware VF allocation path references `binary->vf_frame_info` even when firmware is present, a potential null issue.

Test signals: multi-pipeline map/unmap, stage auto-allocation cleanup on failure, continuous/offline port config bits per pipe id, start/stop when SP is stopped, and `has_stopped` with SP group DMEM state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/pipeline/src/pipeline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/interface/ia_css_queue.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/interface/ia_css_queue.h

Purpose: public queue abstraction for local host queues and remote queues in host/SP/ISP memory.

Important types/APIs: `ia_css_queue_local`, opaque `ia_css_queue_t`, init for local/remote queues, uninit, enqueue/dequeue, empty/full checks, used/free space, peek, and size query.

Control flow/state: local queues wrap host circular-buffer descriptors/elements. Remote queues store location/proc/address metadata and use `queue_access` to load/store descriptors and items during each operation.

Dependencies/integration: `ia_css_queue_comm.h`, `queue_access.h`, platform/type support, and circular-buffer helpers. Eventq and buffer queues rely on this API.

Risks: remote operations are not atomic across descriptor load, item access, and descriptor store; external synchronization or single-producer/single-consumer assumptions matter. The header exposes implementation internals by including `../src/queue_access.h`.

Test signals: local queue wraparound, remote SP/HOST queue enqueue/dequeue, full/empty errors, peek boundary, and size/free/used consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/interface/ia_css_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/interface/ia_css_queue_comm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/interface/ia_css_queue_comm.h

Purpose: common queue constants and remote descriptor ABI.

Important definitions: queue locations (`HOST`, `SP`, `ISP`), queue types (`LOCAL`, `REMOTE`), `IA_CSS_MIN_ELEM_COUNT`, `IA_CSS_DMA_XFER_MASK`, and `ia_css_queue_remote_t` with descriptor/element addresses, location, and processor id.

Control flow/state: no logic. The remote descriptor tells queue operations where and how to access circular-buffer metadata/items.

Dependencies/integration: uses circular-buffer types and is consumed by queue init/access, event queues, and SP/host shared queues.

Risks: location/type constants are macros rather than enums for compactness, so invalid values can reach runtime. Minimum element count reflects DMA alignment and must match SP-side queue layout.

Test signals: ABI layout compatibility, remote init for each supported location, ISP location returning unsupported in access layer, and alignment assumptions for DDR queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/interface/ia_css_queue_comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue.c

Purpose: implements queue operations over local circular buffers and remote SP/HOST queue memory.

Important functions: local/remote init, uninit, enqueue, dequeue, full/empty checks, free/used space, peek, and get size.

Control flow: local paths call `ia_css_circbuf_*` directly. Remote paths load a circular-buffer descriptor with selected ignore flags, check full/empty/bounds, load/store an element when needed, update `start` or `end`, and store only changed descriptor fields. Size query can skip mutable indices and read descriptor size only.

State/persistence: local queue state lives in caller-provided descriptor/element buffers. Remote queue state persists in SP DMEM or HMM memory at addresses in the queue handle.

Dependencies/integration: `queue_access.c`, circular-buffer helpers, math support. Event/eventq and buffer queue code build on this layer.

Risks: remote operations are multi-step and not protected from concurrent writers. `ia_css_queue_peek` treats `offset > num_elems` as invalid, which allows `offset == num_elems` even though that is past the last valid element. `ia_css_queue_get_size` returns 0 for unknown queue type.

Test signals: wraparound enqueue/dequeue, remote descriptor zero-size `-EDOM`, peek offset boundary, unsupported ISP remote access, and consistency under producer/consumer sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue_access.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue_access.c

Purpose: low-level load/store helpers for remote queue descriptors and elements.

Important functions: `ia_css_queue_load`, `ia_css_queue_store`, `ia_css_queue_item_load`, and `ia_css_queue_item_store`.

Control flow: SP-location descriptor fields are accessed byte-by-byte through `sp_dmem_load/store_uint8` respecting ignore flags; HOST location transfers whole descriptors/elements via `hmm_load/store`; ISP location returns `-ENOTSUPP`. Item access uses element address plus `position * sizeof(ia_css_circbuf_elem_t)`.

State/persistence: no owned state. It mutates remote queue memory through SP DMEM or HMM operations.

Dependencies/integration: HMM, SP DMEM accessors, circular-buffer types, and queue handle layout from `queue_access.h`.

Risks: SP descriptor `size == 0` returns `-EDOM` as a workaround for transient bad reads to prevent division by zero. Position is `u8`, so queue sizes/indices must fit. No memory barriers or locking are visible around remote descriptor/item updates.

Test signals: descriptor field ignore masks, SP transient zero-size handling, host HMM transfer correctness, item offset calculation, ISP unsupported path, and invalid pointer returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue_access.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue_access.h

Purpose: internal queue handle layout and remote access API declarations.

Important definitions/types: descriptor ignore flags and combined masks, `QUEUE_CB_DESC_INIT`, and `struct ia_css_queue` with type/location/proc id plus either local circular-buffer state or remote descriptor/element addresses.

Control flow/state: the macro initializes circular-buffer descriptors to zero before selective remote loads. Function declarations are implemented in `queue_access.c` and used by `queue.c`.

Dependencies/integration: depends on errno, type support, queue communication constants, and circular-buffer types.

Risks: public `ia_css_queue.h` includes this internal header, so changing `struct ia_css_queue` affects all users. Ignore flags must remain within `QUEUE_IGNORE_DESC_FLAGS_MAX` or assertions fire in access code.

Test signals: macro initialization behavior, ignore-mask combinations, ABI size/layout of `ia_css_queue_t`, and remote init populating the expected union fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/src/queue_access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/interface/ia_css_rmgr.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/interface/ia_css_rmgr.h

Purpose: top-level resource-manager interface and inline/extern storage-class control for resource pools.

Important APIs/macros: `ia_css_rmgr_init`, `ia_css_rmgr_uninit`, `STORAGE_CLASS_RMGR_H`, `STORAGE_CLASS_RMGR_C`, and the documented per-resource interface pattern for init/uninit/acquire/release/refcount. It includes `ia_css_rmgr_vbuf.h`.

Control flow/state: public init/uninit orchestrate concrete vbuf pools in `rmgr.c`; the header itself owns no state.

Dependencies/integration: depends on CSS error definitions and vbuf resource manager. The storage-class macros allow implementations to be compiled as externs or inlined via `__INLINE_RMGR__`.

Risks: circular inclusion with `ia_css_rmgr_vbuf.h` is intentional but fragile. Adding new resource types requires consistent naming and storage-class usage.

Test signals: both inline and non-inline builds, initialization failure unwinding, and availability of vbuf pool APIs through the top-level header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/interface/ia_css_rmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/interface/ia_css_rmgr_vbuf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/interface/ia_css_rmgr_vbuf.h

Purpose: declares virtual-buffer resource handles, pools, global pools, and refcounted acquire/release APIs.

Important types/APIs: `ia_css_rmgr_vbuf_handle` with HMM pointer, refcount, and size; `ia_css_rmgr_vbuf_pool` with copy-on-write/recycle flags, size/index, and handle table; global pools `vbuf_ref`, `vbuf_write`, and `hmm_buffer_pool`; pool init/uninit/acq/rel and refcount retain/release functions.

Control flow/state: implementation is elsewhere, but the model supports reusable vbuf handles with reference counts and pool-level policies.

Dependencies/integration: included by top-level `ia_css_rmgr.h`, depends on CSS types and `ia_css_ptr`. `rmgr.c` initializes/uninitializes all three global pools.

Risks: `u8 count` can overflow if retain/release discipline breaks. Global pool pointers must be initialized before `ia_css_rmgr_init` and remain valid through uninit.

Test signals: pool init/uninit, acquire/release recycle behavior, refcount retain/release including final free, copy-on-write policy, and error handling for null handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/interface/ia_css_rmgr_vbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/src/rmgr.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/src/rmgr.c

Purpose: top-level resource-manager lifecycle wrapper.

Important functions: `ia_css_rmgr_init` initializes `vbuf_ref`, then `vbuf_write`, then `hmm_buffer_pool`; on any failure it calls `ia_css_rmgr_uninit`. `ia_css_rmgr_uninit` uninitializes pools in reverse order: HMM buffer, write vbuf, ref vbuf.

Control flow/state: state lives inside the global pools declared in `ia_css_rmgr_vbuf.h`. This file only sequences lifecycle calls and performs rollback.

Dependencies/integration: depends on vbuf pool functions from the resource-manager implementation. Higher-level CSS initialization should call this before using vbuf resources.

Risks: no null checks for global pool pointers are visible here; the pool implementation must tolerate them or callers must initialize globals first. Partial init rollback depends on uninit being safe for not-yet-initialized pools.

Test signals: successful init/uninit ordering, failure injection at each pool init step, idempotent uninit behavior, and resource leak checks after rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/src/rmgr.c -->
