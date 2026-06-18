# sources/distributed-fs/ceph-client/tools/perf/util/include/linux/linkage.h

Purpose: perf tools copy of kernel linkage annotation macros needed by imported assembly, especially x86 library assembly. It gives assembler sources macros for global/local/weak function labels, alignment, type, size, aliases, and PIC aliases without depending on the full kernel header stack.

Important APIs and types: defines `ASM_NL`, `__ALIGN`, `__ALIGN_STR`, `SYM_T_FUNC`, `SYM_A_ALIGN`, `SYM_L_GLOBAL/WEAK/LOCAL`, `ALIGN`, generic `SYM_ENTRY`, `SYM_START`, `SYM_END`, `SYM_ALIAS`, function-specific `SYM_FUNC_START*`, `SYM_FUNC_END`, `SYM_FUNC_ALIAS*`, `SYM_FUNC_ALIAS_MEMFUNC`, `SYM_TYPED_START`, `SYM_TYPED_FUNC_START`, and `SYM_PIC_ALIAS`.

Control flow: compile/assembly macro expansion only. Macro pairs emit symbol declarations and labels at start/end points and calculate `.size` metadata via assembler expressions.

State and persistence: no runtime state. Generated object metadata persists into object files through symbol type/size/alias directives.

Dependencies and integration: compatible with GNU assembler syntax and kernel imported assembly. The comments note a simplified non-CFI `SYM_TYPED_START` behavior for tools.

Risks: alignment is fixed to `.align 4,0x90`, which is x86-oriented. Variadic macro syntax and assembler directives assume a compatible assembler. Divergence from kernel linkage macros can break newly imported assembly that expects newer semantics.

Test signals: assembly build tests for imported perf routines, symbol table inspection for function type/size/alias correctness, and link tests around PIC aliases where used.
