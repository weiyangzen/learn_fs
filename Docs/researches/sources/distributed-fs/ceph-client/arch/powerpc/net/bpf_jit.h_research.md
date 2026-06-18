# sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit.h

## Purpose
This header defines shared infrastructure for the PowerPC BPF JIT compiler. It provides instruction emission macros, immediate-loading helpers, branch range handling, condition-code constants, code generation context, private-stack guard constants, and cross-file function prototypes.

## Important APIs, Types, And Functions
Key macros include `EMIT`, `PPC_JMP`, `PPC_BCC_SHORT`, `PPC_BCC_CONST_SHORT`, `PPC_BCC`, `PPC_LI32`, `PPC_LI64`, `PPC_LI_ADDR`, and `PPC64_LOAD_PACA`. `struct codegen_context` tracks emitted instruction index, seen registers/features, stack sizes, BPF-to-PPC register mapping, exception table index, alternate exit, arena bases, subprogram/exception flags, and private stack state. Feature bits include `SEEN_FUNC` and `SEEN_TAILCALL`.

## Control Flow
The macros either emit real instructions when `image` is non-null or advance `ctx->idx` conservatively in sizing passes. Branch macros validate offset ranges and synthesize long conditional branches by inverting the condition and emitting an unconditional branch when needed. Immediate loaders use shorter encodings when possible but reserve worst-case length during dry runs.

## State And Persistence
The header does not own global state, but `codegen_context` is the persistent per-compile state passed across prologue, body, epilogue, trampoline, and exception-table generation.

## Dependencies And Integration Points
It depends on PPC opcode helpers, BPF register constants, kernel branch-range helpers, PACA layout, and text patching conventions. It is shared by the common JIT driver and 32/64-bit backends.

## Risks And Test Signals
Risks include dry-run instruction counts diverging from real emission, branch range validation bugs, incorrect ABI handling for function descriptors and TOC/PACA, and register usage tracking errors. Test signals include BPF selftests with large programs, long jumps, helper calls, tail calls, trampoline attachment, private stack programs, and both PPC32/PPC64 builds.
