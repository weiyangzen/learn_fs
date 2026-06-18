# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_pipe.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_pipe.h` declares internal pipe-graph debug helpers for graph prologue/epilogue, pipeline stage dumping, SP raw-copy frame dumping, and stream-config dumping.

Important APIs, types, and functions: Important local symbols: `ia_css_debug_pipe_graph_dump_prologue`, `ia_css_debug_pipe_graph_dump_epilogue`, `ia_css_debug_pipe_graph_dump_stage`, `ia_css_debug_pipe_graph_dump_sp_raw_copy`, `ia_css_debug_pipe_graph_dump_stream_config` Types and constants: No named structs or enums are introduced here.; `_IA_CSS_DEBUG_PIPE_H_`

Control flow: Pipeline diagnostic code calls these functions around stage traversal to emit a graph representation of the active stream/pipe.

State and persistence behavior: Debug state is runtime-only: global `dbg_level`, live pipeline/frame/config pointers passed to dumpers, SP debug state, and hardware diagnostic registers. Output goes to tracing/log sinks but this header does not persist files.

Dependencies and integration points: Debug declarations integrate CSS stream/pipe/frame/binary types, metadata, SP debug state, AtomISP internals, and low-level hardware diagnostics.

Risks and edge cases: The API accepts live pipeline-stage and frame pointers, so dump code must tolerate partially configured or torn-down pipelines.

Test signals: Validate trace-level gating, format-string coverage, dumpers with NULL or inactive pipeline members where permitted, SP sleep/wake debug paths, DMA debug-mode toggles, pipe graph output, and high-frequency event polling without log flooding.
