# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/special.c

Purpose: x86 architecture hooks for alternatives, jump-table discovery, and CPU feature naming.

Important APIs/types/functions: `arch_handle_alternative()` normalizes nested alternative original lengths. `arch_support_alt_relocation()` allows alternative relocations. `arch_find_switch_table()` detects x86 switch tables from text relocations into rodata and returns the first table relocation. `arch_cpu_feature_name()` maps feature numbers through generated `cpu-feature-names.c`.

Control flow: switch-table discovery checks an instruction's relocations for rodata section symbols, adjusts PC-relative offsets, rejects named data except C jump-table sections, resolves table entry relocations, and marks rare RIP-relative table patterns by enabling `file->ignore_unreachables`.

State and persistence behavior: mutates in-memory alternative records and `objtool_file.ignore_unreachables`; no direct ELF writes.

Dependencies and integration points: used by generic special parsing, jump-table analysis in `check.c`, alternative disassembly naming, and x86 cpufeature definitions.

Risks: static state in `arch_handle_alternative()` assumes ordered parsing. Switch-table heuristics intentionally trade precision for kernel compiler patterns and can miss or overaccept unusual generated code.

Test signals: x86 switch-heavy objects, C jump-table sections, nested alternatives, and disassembly of feature-named alternatives should produce stable alternative graphs and no false unreachable warnings for known RIP-relative quirks.
