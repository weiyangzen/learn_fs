# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/disas.h

Purpose: Declares the optional objtool disassembly formatting interface used for diagnostics, tracing, and readable instruction dumps.

Important APIs/types/functions: `disas_context_destroy`, `disas_warned_funcs`, `disas_funcs`, `disas_info_init`, `disas_insn`, `disas_print_info`, `disas_print_insn`, `_DISAS_H`, `alternative`, `disas_context`, `disassemble_info`.

Control flow: When disassembly support is compiled in, callers create a context, disassemble functions/instructions, and print annotated output; stub inlines make calls no-ops otherwise.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Integrates with binutils disassembler types, `struct objtool_file`, `struct instruction`, alternatives, and trace/warn macros.

Risks: Stub behavior can hide missing disassembly during diagnostics; context lifetime must bracket all formatted instruction use.

Test signals: Run objtool with disassembly-enabled warnings/tracing and with a build lacking disassembler support.

Source coverage: researched from the complete local file (82 lines, 2292 bytes).
