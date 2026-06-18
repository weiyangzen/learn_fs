# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/trace.h

Purpose: Provides optional objtool tracing macros and CFI/alternative trace printers for debugging checker state transitions.

Important APIs/types/functions: `trace_enable`, `trace_disable`, `trace_depth_inc`, `trace_depth_dec`, `trace_insn_state`, `trace_alt_begin`, `trace_alt_end`, `_TRACE_H`, `TRACE`, `TRACE_ADDR`, `TRACE_INSN`, `TRACE_INSN_STATE`.

Control flow: Trace macros gate output on global `trace`, adjust indentation through `trace_depth`, print instruction state deltas, and annotate alternative traversal begin/end.

State and persistence behavior: Global `trace` and `trace_depth` hold process-local diagnostic state only.

Dependencies and integration points: Depends on checker instruction/CFI structures, disassembly printers, arch register names, and stderr diagnostics.

Risks: Only compiled when trace support is enabled; static register-name buffer requires duplication before nested formatting; trace depth must balance on alternative paths.

Test signals: Enable trace for functions with register-state changes, exception alternatives, jump labels, and nested alternatives.

Source coverage: researched from the complete local file (142 lines, 3391 bytes).
