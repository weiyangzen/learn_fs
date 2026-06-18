# sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp32.c

## Purpose
This file is the 32-bit PowerPC eBPF JIT backend. It maps 64-bit eBPF registers onto pairs of 32-bit PPC registers, builds PPC32 prologue/epilogue code, emits helper calls and tail calls, and translates BPF ALU, load/store, atomic, endian, branch, call, and exit instructions into PPC opcodes.

## Important APIs, Types, And Functions
Backend entry points include `bpf_jit_init_reg_mapping()`, `bpf_jit_realloc_regs()`, `prepare_for_fsession_fentry()`, `store_func_meta()`, `bpf_jit_build_prologue()`, `bpf_jit_build_epilogue()`, `bpf_jit_emit_func_call_rel()`, and `bpf_jit_build_body()`. Internal helpers include `bpf_jit_stack_offsetof()`, `bpf_has_stack_frame()`, `bpf_jit_emit_common_epilogue()`, and `bpf_jit_emit_tail_call()`.

## Control Flow
Register mapping assigns each eBPF 64-bit register to an even/odd high-low PPC register pair, with nonvolatile registers used for callee-saved BPF state. The prologue emits an attachable NOP, initializes or preserves tail-call count, creates a stack frame when needed, saves nonvolatile registers, maps input `r3` into BPF R1, and sets the BPF frame pointer. The body loop records `addrs[]`, tracks seen registers, performs a MOV-combine optimization, and emits per-opcode instruction sequences. Unsupported 64-bit division/modulo cases return `-EOPNOTSUPP` except power-of-two immediates. The epilogue moves BPF R0 into PPC return register, restores state, returns, and appends fentry stubs.

## State And Persistence
Compile-time state lives in `codegen_context`: seen registers, stack size, register map, emitted index, and feature flags. Runtime state is the generated machine code, BPF stack frame, saved nonvolatile registers, and tail-call counter slot.

## Dependencies And Integration Points
It depends on common JIT macros, PPC raw opcode helpers, BPF verifier flags such as `verifier_zext`, BPF helper address resolution, exception-table support for `BPF_PROBE_MEM`, and the common compiler driver.

## Risks And Test Signals
Risks include high/low word ordering mistakes, signed versus unsigned branch errors, dry-run and real-pass divergence, unsupported instruction handling, atomic memory-ordering mistakes, probe-memory fixup offsets, and stack-frame save/restore bugs. Test signals include BPF ALU32/ALU64 selftests, endian conversion, signed comparisons, atomics, probe-memory loads, tail calls, helper calls, verifier zext and non-zext modes, and PPC32 JIT build/runtime selftests.
