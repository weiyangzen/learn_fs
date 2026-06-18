# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/ppc_asm.h

## Purpose
`ppc_asm.h` is a substantial copied powerpc assembler helper header. It supplies register names, function-label macros, save/restore sequences, address-loading helpers, stack-frame layout, feature-fixup hooks, timebase/TLB/cache helpers, and endian-aware vector save/restore macros used by selftest assembly.

## Important APIs, Types, and Functions
Important macros include `FUNC_START`, `FUNC_END`, `_GLOBAL`, `_GLOBAL_TOC`, `SAVE_GPRS`, `REST_GPRS`, `ZEROIZE_GPRS`, `SAVE_FPR`, `SAVE_VR`, `SAVE_VSR`, HMT priority macros, `LOAD_REG_IMMEDIATE`, `LOAD_REG_ADDR`, `PPC_CREATE_STACK_FRAME`, `MFTB`, `TLBSYNC`, `tophys`, `tovirt`, `MTMSRD`, and the `r0` through `r31` register aliases.

## Control Flow and State
The header has no standalone runtime flow. Its macros expand into assembly that saves/restores architectural registers, builds ABI-correct stack frames, loads addresses under TOC or PC-relative models, and emits feature-fixup metadata where configured. State affected by generated code includes GPRs, FPRs, vector registers, LR, CR, stack memory, timebase reads, and TLB/cache instructions.

## Dependencies and Integration Points
It depends on the local `linux/stringify.h`, `asm/asm-compat.h`, `asm/processor.h`, `asm/ppc-opcode.h`, `asm/firmware.h`, `asm/feature-fixups.h`, and `asm/extable.h` shims. It is included by PMU and ptrace assembly helpers copied from kernel-style code.

## Risks and Test Signals
Risks are high because macro changes alter hand-written assembly ABI behavior, symbol visibility, endian handling, or register save layout. Signals are successful assembly across 64-bit selftests and correct runtime behavior of loops, ptrace GPR helpers, and exception-table primitive tests.
