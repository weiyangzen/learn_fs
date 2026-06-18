# sources/distributed-fs/ceph-client/arch/mips/kernel/probes-common.h

## Purpose
Provides common instruction classification helpers for MIPS kprobes/uprobes-style code. It declares compact-branch detection and implements delay-slot detection for classic MIPS branch/jump encodings.

## Important APIs, Types, and Functions
- `__insn_is_compact_branch()` is declared for external implementation.
- `__insn_has_delay_slot()` inspects `union mips_instruction` opcode/function fields and returns whether the instruction has a branch delay slot.

## Control Flow
The inline helper switches first on the primary opcode, then on nested function/rt fields for `spec_op` and `bcond_op`. It recognizes `jr`, `jalr`, conditional branches, branch-likely variants, `j`, `jal`, FPU/coprocessor branch opcodes, and Octeon bbit encodings when configured.

## State and Persistence
No state. Pure instruction classification.

## Dependencies and Integration Points
Depends on `asm/inst.h` instruction unions and opcode constants. Consumers are probe implementations that need to know whether placing or single-stepping a probe must account for a delay slot.

## Risks
Incomplete opcode coverage can make probes mishandle control flow. MIPS revisions with compact branches or vendor encodings require coordination with `__insn_is_compact_branch()` and architecture-specific configs. Returning true for all `cop1_op` is conservative but broad.

## Test Signals
Probe tests on branches, branch-likely instructions, `jr/jalr`, FPU branches, and Octeon bbit instructions should single-step correctly and not execute wrong delay-slot instructions.
