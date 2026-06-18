# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/src/ia_css_debug.c

Purpose: host-side diagnostics for the CSS/AtomISP runtime. It formats stream/frame enums, dumps FIFO/SP/pipeline/ISP parameter state, emits graphviz-style pipeline graphs, controls SP sleep/wake/debug DMA bits, and reads trace buffers/PC registers.

Important APIs/functions: `ia_css_debug_dtrace`, trace-level setters, FIFO dump helpers, `ia_css_debug_binary_print`, `ia_css_debug_frame_print`, `ia_css_debug_dump_sp_sw_debug_info`, `ia_css_debug_dump_isp_params`, `ia_css_debug_pipe_graph_dump_*`, config dump helpers, `ia_css_debug_dump_trace`, and `ia_css_debug_pc_dump`.

Control flow: most entry points are read-only dump routines that translate runtime structs or hardware/SP memory into debug output. Pipe graph generation is stateful: prologue initializes graph state, stage/raw-copy functions add nodes/edges, and epilogue emits deferred input-system/sensor nodes and resets temporary buffers. Trace dumping validates tracer headers, reads cyclic trace buffers, handles wraparound, then prints decoded entries.

State/persistence: global debug level `dbg_level` comes from the debug subsystem. This file owns static pipe-graph state (`pg_inst`, `dot_id_input_bin`, `ring_buffer`) and some static trace cursors/sample counters. It reads persistent SP DMEM and device registers but does not own them.

Dependencies/integration: tightly coupled to `ia_css_pipeline`, `ia_css_frame`, `ia_css_isp_param`, `sh_css_sp`, buffer queues, ISP kernel parameter dumpers, FIFO monitor, SP/ISP register accessors, and compile-time `SP_DEBUG`/`TRACE_ENABLE_*` feature flags.

Risks: many routines assume non-NULL objects and valid enum values via `assert`; malformed runtime state can produce truncated graph labels or invalid offsets. Debug paths read live hardware/SP memory without locking, so output can be inconsistent during active streaming. The DOT graph builder uses fixed-size static buffers and shared state, so concurrent callers can corrupt output.

Test signals: exercise stream/pipe/frame dumps with representative formats, verify DOT prologue/stage/epilogue ordering, compile with each `SP_DEBUG` mode, and use hardware/simulator traces to confirm wraparound and invalid-version handling.
