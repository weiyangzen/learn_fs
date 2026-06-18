# sources/distributed-fs/ceph-client/arch/mips/net/bpf_jit_comp32.c

## Purpose
Implements the MIPS o32, 32-bit CPU backend for the shared eBPF JIT compiler. It translates verifier-accepted eBPF instructions into MIPS32 instruction streams while preserving 64-bit eBPF register semantics with native register pairs.

## Important APIs, Types, And Functions
The externally used JIT hooks are `build_prologue`, `build_epilogue`, and `build_insn` from the shared MIPS JIT framework. The central mapping is `bpf2mips32[][2]`, with helpers `lo()` and `hi()` selecting the low/high native register by endianness. Arithmetic emitters include `emit_alu_i64`, `emit_alu_r64`, `emit_shift_i64`, `emit_shift_r64`, `emit_mul_i64`, `emit_mul_r64`, `emit_divmod_r64`, `emit_bswap_r64`, and `emit_trunc_r64`. Memory and atomic paths are `emit_ldx`, `emit_stx`, `emit_atomic_r32`, `emit_atomic_r64`, `emit_cmpxchg_r32`, and `emit_cmpxchg_r64`. Branching and calls are handled by `emit_jmp_i64`, `emit_jmp_r64`, `emit_call`, and `emit_tail_call`.

## Control Flow
`build_insn` dispatches on the eBPF opcode class and emits one or more native instructions. 32-bit ALU opcodes operate on the low register and then rely on verifier-provided or local zero extension. 64-bit opcodes route through register-pair helpers for carry/borrow, cross-word shifts, multiply, divide/modulo helper calls, byte swaps, and comparisons. Calls resolve a fixed helper address through `bpf_jit_get_func_addr`, push stack-passed o32 arguments and caller-saved registers as needed, and emit `jalr`. Tail calls check array bounds, decrement the tail-call counter stored in the caller-reserved stack area, fetch the target program's `bpf_func`, skip the prologue initialization bytes, and jump through the normal epilogue path.

## State And Persistence
Generated code state is held in `struct jit_context`: clobbered/accessed register bitmaps, stack sizing, BPF instruction index, and emitted offsets. Runtime state is only the generated stack frame, including saved callee registers, local eBPF stack, spill space for caller-saved registers and stack arguments, and a tail-call counter stored at the top of the inherited o32 frame. No filesystem or durable persistence is involved.

## Dependencies And Integration Points
Depends on `linux/filter.h`, `linux/bpf.h`, `linux/math64.h`, MIPS CPU feature probes, uasm emit macros, and common helpers in `bpf_jit_comp.h`. It integrates with the eBPF verifier's `verifier_zext` contract, generic BPF helper address resolution, kernel atomic APIs, `div64_u64`, `atomic64_*`, and MIPS ABI rules for o32 argument passing, return registers, delay slots, and stack alignment.

## Risks And Edge Cases
The highest-risk areas are register-pair endianness, o32 stack argument layout, callee/caller save masks, branch-distance handling via `finish_jmp`, and tail-call prologue skip constants. CPUs without MIPS II load-delay behavior need explicit `nop`s. CPUs without LL/SC fall back to C atomic helpers, requiring correct caller-saved preservation and result exclusion. 64-bit div/mod helper calls must not clobber live eBPF state. Atomic compare-exchange has big-endian result-register special handling. Invalid or unsupported opcodes return `-EINVAL`, `-EFAULT`, or `-E2BIG`, which should force interpreter fallback rather than unsafe code.

## Test Signals
Useful signals are BPF selftests on 32-bit MIPS for ALU64 carry/borrow, unaligned-sized loads/stores within verifier constraints, atomics with and without fetch, `cmpxchg`, tail calls, helper calls with more than two 64-bit arguments, endian conversion, and long branches. Build coverage must include big- and little-endian MIPS32, LL/SC and non-LL/SC configurations, and older ISA variants with load delays.
