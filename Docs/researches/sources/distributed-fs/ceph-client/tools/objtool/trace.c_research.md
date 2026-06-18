# sources/distributed-fs/ceph-client/tools/objtool/trace.c

Purpose: Provides optional objtool tracing macros and CFI/alternative trace printers for debugging checker state transitions.

Important APIs/types/functions: `trace_cfi_reg`, `trace_cfi_reg_val`, `trace_cfi_reg_ref`, `trace_insn_state`, `trace_alt_begin`, `trace_alt_end`, `TRACE_CFI_ATTR`, `TRACE_CFI_ATTR_BOOL`, `TRACE_CFI_ATTR_NUM`, `CFI_REG_NAME_MAXLEN`, `TRACE_CFI_REG_VAL`, `TRACE_CFI_REG_REF`.

Control flow: Trace macros gate output on global `trace`, adjust indentation through `trace_depth`, print instruction state deltas, and annotate alternative traversal begin/end.

State and persistence behavior: Global `trace` and `trace_depth` hold process-local diagnostic state only.

Dependencies and integration points: Depends on checker instruction/CFI structures, disassembly printers, arch register names, and stderr diagnostics.

Risks: Only compiled when trace support is enabled; static register-name buffer requires duplication before nested formatting; trace depth must balance on alternative paths.

Test signals: Enable trace for functions with register-state changes, exception alternatives, jump labels, and nested alternatives.

Source coverage: researched from the complete local file (204 lines, 5424 bytes).
