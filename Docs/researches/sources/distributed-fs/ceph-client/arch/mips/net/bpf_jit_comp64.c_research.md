# sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp64.c

## Purpose
Implements the MIPS n64, 64-bit CPU backend for the shared eBPF JIT compiler. Unlike the 32-bit backend, each eBPF register maps to one native 64-bit MIPS register, with extra JIT registers for tail-call count and zero-extension masks.

## Important APIs, Types, And Functions
The exported JIT hooks are `build_prologue`, `build_epilogue`, and `build_insn`. `bpf2mips64[]` maps eBPF registers to native registers; `JIT_REG_TC` holds the tail-call counter and `JIT_REG_ZX` holds a 32-bit mask for zero extension on older MIPS64. Major emitters include `emit_sext`, `emit_zext`, `emit_mov_i64`, `emit_alu_i64`, `emit_alu_r64`, `emit_bswap_r64`, `emit_trunc_r64`, `emit_ldx`, `emit_stx`, `emit_atomic_r64`, `emit_cmpxchg_r64`, `emit_call`, and `emit_tail_call`.

## Control Flow
`build_insn` dispatches eBPF opcodes into native MIPS64 emissions. For BPF_ALU 32-bit arithmetic it explicitly sign-extends operands before operations that require it and zero-extends results when the verifier has not inserted zext. BPF_ALU64 routes directly through dword operations, including MIPS64r6-specific multiply/divide/modulo forms when available. Memory access uses byte/half/word/dword load-store opcodes. Atomics use LL/SC loops for 64-bit operations and common 32-bit LL/SC helpers for word atomics. Helper calls save JIT caller-saved registers, jump through a masked fixed address, then restore the zero-extension mask register if it was live. Tail calls use the in-register counter, fetch the target `bpf_prog`, skip the first prologue instruction, and jump via the epilogue.

## State And Persistence
State is contained in the generated native stack frame and `jit_context`. The stack frame saves only clobbered callee registers, local eBPF stack, and any reserved caller-saved spill area. Tail-call count is initialized into a caller-saved register rather than persisted on the stack unless the register is accessed and marked for preservation. No persistent storage is touched.

## Dependencies And Integration Points
Depends on common MIPS JIT helpers in `bpf_jit_comp.h`, uasm emission macros, MIPS64 ISA feature probes, generic BPF helper resolution, LL/SC helper macros, Linux BPF verifier zero-extension behavior, and n64 ABI stack and register rules. It must line up with `struct bpf_array` and `struct bpf_prog` layouts for tail calls.

## Risks And Edge Cases
The main correctness risks are MIPS64 sign-extension semantics for 32-bit operations, conditional use of `JIT_REG_ZX`, helper-call address masking with `JALR_MASK`, tail-call skip length, and preserving caller-saved registers around helper calls. R4000 multiplication workarounds, MIPS64r6 instruction selection, branch-distance handling, and LL/SC retry offsets are CPU-sensitive. The epilogue sign-extends the 32-bit return value in the jump delay slot, so return-width behavior must match the shared JIT contract.

## Test Signals
BPF selftests should exercise 32-bit ALU zext and sign-sensitive operations, ALU64 multiply/divide/modulo on r6 and non-r6 CPUs, atomics, `cmpxchg`, tail-call chains, helper calls, endian conversion, and long conditional jumps. Cross-builds for MIPS64 r1/r2/r6 and configurations without verifier zext assumptions are valuable.
