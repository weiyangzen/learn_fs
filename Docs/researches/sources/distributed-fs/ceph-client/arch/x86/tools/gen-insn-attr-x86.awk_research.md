<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/gen-insn-attr-x86.awk -->
# sources/distributed-fs/ceph-client/arch/x86/tools/gen-insn-attr-x86.awk

## Purpose
`gen-insn-attr-x86.awk` generates x86 instruction attribute tables from `x86-opcode-map.txt` for the in-kernel/tools instruction decoder.

## Important APIs, types, and functions
Important routines include `check_awk_implement()`, `clear_vars()`, `semantic_error()`, `print_table()`, `convert_operands()`, and table emission logic for primary, escape, group, AVX, EVEX, XOP, and prefix tables.

## Control flow
It parses table directives, tracks opcode variants, operand/immediate/modrm attributes, prefix-specific tables, group references, escape maps, and final table pointer arrays. Semantic errors abort generation when opcode maps redefine entries or use unknown operands.

## State and persistence behavior
All state is AWK arrays such as `table`, `lptable*`, `etable`, `gtable`, `atable`, and `xoptable`. The persistent artifact is generated `inat-tables.c`.

## Dependencies and integration points
It depends on opcode-map syntax, `asm/inat.h` flag names, AWK formatting correctness, and generated C being included by `insn.c` users.

## Risks and edge cases
Decoder correctness relies on this parser preserving prefix and operand semantics. New ISA encodings can be misdecoded if regex classifications are incomplete.

## Test signals
Signals are successful generation, `insn_decoder_test` against objdump, `insn_sanity` fuzzing, and review of table diffs when opcode maps change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/gen-insn-attr-x86.awk -->
