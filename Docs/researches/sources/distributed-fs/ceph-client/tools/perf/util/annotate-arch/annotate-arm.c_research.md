# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arm.c

## Purpose

`annotate-arm.c` creates the ARM architecture descriptor for perf annotation and classifies ARM call/jump instructions.

## Important APIs, Types, and Functions

`struct arch_arm` embeds `struct arch` and stores compiled regexes for call and jump instructions. `arm__associate_instruction_ops` matches instruction names against `blx?` with optional conditions and branch/jump regexes, then associates `call_ops` or `jump_ops`. Public `arch__new_arm` allocates and initializes the descriptor.

## Control Flow and State

Creation sets objdump comment and skip-function characters, installs the associate callback, compiles regexes, and returns `NULL` on allocation or regex failure. Instruction association caches matched ops in the generic arch table.

## Dependencies and Integration Points

It depends on regex, generic annotate/disasm ops, and ARM objdump syntax. Annotation uses it to build call graphs and branch semantics in ARM disassembly.

## Risks and Test Signals

Risks are regex incompleteness for ARM/Thumb mnemonics and leaks on partial regex failure. Tests should annotate ARM binaries containing calls, conditional branches, unconditional branches, and non-branch instructions.
