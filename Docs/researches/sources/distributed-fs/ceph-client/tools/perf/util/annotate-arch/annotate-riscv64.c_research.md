# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-riscv64.c

## Purpose
Provides RISC-V 64-bit instruction classification for perf annotate. It maps common call, return, and branch/jump mnemonics to generic annotation operations.

## Important APIs, Types, and Functions
`arch__new_riscv64()` allocates the architecture descriptor, names it `riscv`, sets `objdump.comment_char` to `#`, and installs `riscv64__associate_ins_ops()`.
`riscv64__associate_ins_ops()` maps `jal`, `jr`, and `call` prefixes to `call_ops`, `ret` to `ret_ops`, and any `j*` or `b*` mnemonic to `jump_ops`.

## Control Flow
The function performs prefix checks in call/return/jump order, then caches matched operations via `arch__associate_ins_ops()`. The generic jump/call operand parsers are used; this file does not parse RISC-V operands itself.

## State and Persistence
Only the `struct arch` allocation and operation cache are persisted for the process lifetime. No per-line allocations are made here.

## Dependencies and Integration Points
Uses `../disasm.h` and the generic operation instances. Integrates with common annotate rendering and jump-target bookkeeping by assigning `ins_ops`.

## Risks
Classifying `jr` as a call is conservative for link-register idioms but can misrepresent plain indirect jumps. Prefix matching can catch aliases unintentionally and miss compressed or assembler-specific mnemonics not represented by these prefixes.

## Test Signals
Annotate RISC-V functions containing `jal`, `call`, `ret`, conditional branches, and indirect jumps; verify marker selection and local branch arrows.
