# sources/distributed-fs/ceph-client/tools/arch/x86/tools/gen-insn-attr-x86.awk

## Purpose
Generates `inat-tables.c`, the x86 instruction attribute tables used by the decoder, from `x86-opcode-map.txt`.

## APIs, Types, and Functions
Major functions include `check_awk_implement()`, `clear_vars()`, `semantic_error()`, `array_size()`, `print_table()`, `add_flags()`, and `convert_operands()`. The generated output includes primary, escape, group, AVX, and XOP tables plus table pointer arrays or boot-compressed initialization code.

## Control Flow, State, and Persistence
`BEGIN` initializes regexes and maps for immediates, prefixes, VEX/EVEX/XOP tags, REX/REX2 tags, and table counters. Table directives (`Table`, `Referrer`, `AVXcode`, `XOPcode`, `GrpTable`, `EndTable`) control which generated table is active. Opcode lines are parsed into flags for immediate sizes, ModRM, groups, forced/invalid 64-bit, prefixes, VEX/EVEX/XOP eligibility, and last-prefix variants. `END` emits pointer arrays for all discovered table IDs.

## Dependencies and Integration
Consumes the kernel x86 opcode map and emits C using constants from `inat.h` and `insn.h`. `lib/inat.c` includes the generated file.

## Risks and Test Signals
Risks include fragile awk parsing, unsupported operand tokens, duplicate opcode definitions, missing EVEX/REX2 annotations, and awk implementation differences. Test signals are generator runs with gawk/awk, generated C compilation, semantic-error tests for malformed opcode maps, and decoder golden tests over generated attributes.
