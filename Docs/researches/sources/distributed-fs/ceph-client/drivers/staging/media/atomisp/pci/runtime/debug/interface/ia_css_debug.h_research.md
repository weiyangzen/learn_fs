# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug.h` declares the broad CSS debug and diagnostics API: trace levels/macros, global dtrace level control, binary/frame/resolution/config dumpers, SP sleep/wake controls, FIFO and MIPI diagnostics, DMA debug-mode controls, PC dumps, hang-status dumps, and external command handling.

Important APIs, types, and functions: Important local symbols: `__printf`, `ia_css_debug_set_dtrace_level`, `ia_css_debug_get_dtrace_level`, `ia_css_debug_dump_gac_state`, `ia_css_debug_dump_sp_sw_debug_info`, `ia_css_debug_print_sp_debug_state`, `ia_css_debug_binary_print`, `ia_css_debug_sp_dump_mipi_fifo_high_water`, `ia_css_debug_dump_pif_a_isp_fifo_state`, `ia_css_debug_dump_pif_b_isp_fifo_state`, `ia_css_debug_dump_str2mem_sp_fifo_state`, `ia_css_debug_dump_all_fifo_state`, `ia_css_debug_frame_print`, `ia_css_debug_enable_sp_sleep_mode` Types and constants: `ia_css_debug_enable_param_dump`; `_IA_CSS_DEBUG_H_`, `IA_CSS_DEBUG_ERROR`, `IA_CSS_DEBUG_WARNING`, `IA_CSS_DEBUG_VERBOSE`, `IA_CSS_DEBUG_TRACE`, `IA_CSS_DEBUG_TRACE_PRIVATE`, `IA_CSS_DEBUG_PARAM`, `IA_CSS_DEBUG_INFO`, `IA_CSS_ERROR`, `IA_CSS_WARNING`

Control flow: Callers use macros such as `IA_CSS_ENTER`, `IA_CSS_ERROR`, and `IA_CSS_LEAVE_ERR_PRIVATE`; those call `ia_css_debug_dtrace()`, which is gated by `dbg_level` and eventually prints through `sh_css_vprint()`.

State and persistence behavior: Debug state is runtime-only: global `dbg_level`, live pipeline/frame/config pointers passed to dumpers, SP debug state, and hardware diagnostic registers. Output goes to tracing/log sinks but this header does not persist files.

Dependencies and integration points: Debug declarations integrate CSS stream/pipe/frame/binary types, metadata, SP debug state, AtomISP internals, and low-level hardware diagnostics.

Risks and edge cases: Tracing is global and can be noisy in polled paths; debug APIs expose low-level controls such as DMA-channel disable/enable that can perturb a live pipeline.

Test signals: Validate trace-level gating, format-string coverage, dumpers with NULL or inactive pipeline members where permitted, SP sleep/wake debug paths, DMA debug-mode toggles, pipe graph output, and high-frequency event polling without log flooding.
