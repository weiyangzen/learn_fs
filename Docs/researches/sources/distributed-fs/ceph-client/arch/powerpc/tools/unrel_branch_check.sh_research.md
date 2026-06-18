# sources/distributed-fs/ceph-client/arch/powerpc/tools/unrel_branch_check.sh

## Purpose
`unrel_branch_check.sh` detects suspicious relative branches from unrelocated early PowerPC code to relocated code beyond the interrupt-vector region.

## Important APIs, Types, And Functions
It consumes objdump, nm, and vmlinux paths, finds `__end_interrupts` and `__start_initialization_multiplatform`, disassembles from kernel start `0xc000000000000000` to `__end_interrupts`, filters branch instructions with sed, normalizes branch targets, and prints warnings for targets past the unrelocated region.

## Control Flow
If `__end_interrupts` is absent, it exits successfully. Otherwise it disassembles early code, removes CTR/LR branches, handles GNU and Clang objdump conditional branch spelling, computes absolute targets for direct and relative branches, skips the one known valid branch to initialization, and emits warnings when a branch lands after `__end_interrupts`.

## State And Persistence
The script is stateless and writes only diagnostics.

## Dependencies And Integration Points
It depends on bash arithmetic, objdump, nm, sed, PowerPC branch encoding ranges, and early kernel symbol names. It is part of post-link validation for head and interrupt-vector code.

## Risks
Parsing disassembly text is fragile across tool versions. The script contains a typo in the unknown-format diagnostic but still identifies the path. Incorrect branch offset sign extension would either miss invalid branches or warn on valid ones. The known-good exception must remain aligned with early boot code.

## Test Signals
Passing output is silent. A problematic branch produces `WARNING: Unrelocated relative branches` followed by source address, branch mnemonic, computed target, and optional symbol.
