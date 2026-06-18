# sources/distributed-fs/ceph-client/arch/arm/nwfpe/entry.S

## Purpose
Provides the assembly entry path from ARM undefined-instruction handling into NWFPE. It dispatches coprocessor 1/2 FPA instructions, invokes the emulator, chains consecutive FP instructions to amortize trap overhead, and returns either to normal exception return or undefined-instruction failure.

## Important APIs, Types, And Functions
Exports `nwfpe_enter`, `call_fpe`, `fp_enter`, and `no_fp`. Uses `EmulateAll`, `arm_check_condition`, user access macros, exception-table fixups, `TI_FPSTATE`, `TI_FLAGS`, optional iWMMXt enabling, and return addresses passed in `r9` and `lr`.

## Control Flow
`call_fpe` loads the faulting user opcode, rejects non-coprocessor or non-FPE coprocessors, handles optional iWMMXt CP0/1 access, and branches to `fp_enter`. `nwfpe_enter` checks ARM condition codes, calls `EmulateAll`, and on success fetches the next user instruction. If the next instruction still looks like FP, it updates saved PC and emulates again; otherwise it returns via `r9`.

## State, Dependencies, And Integration
State modified includes saved user PC/CPSR in `pt_regs`, current thread FP workspace, and user access state. Dependencies include `asm/assembler.h`, opcode endian conversion, exception table machinery, and `fpmodule.c` patching `fp_enter` to `nwfpe_enter`.

## Risks And Test Signals
Risks are incorrect PC advancement, user memory fault fixup bugs, condition-code mis-evaluation, chained instruction overrun, and conflicts with VFP/iWMMXt dispatch. Test signals are undefined-instruction FP traps, conditional FP instructions, faulting instruction fetch, chained FP sequences, big-endian instruction fetch, and iWMMXt coexistence builds.
