
# sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp64.c

## Purpose

This file implements the 64-bit PowerPC eBPF JIT compiler backend. It maps BPF virtual registers to PowerPC GPRs, emits prologue and epilogue code, emits helper/kfunc/BPF-to-BPF calls, supports tail calls, exception-boundary callbacks, private stacks, arena/probe memory, atomic operations, byte swapping, speculation barriers, and the main BPF instruction translation loop.

## Important APIs, Types, And Functions

- `bpf_jit_init_reg_mapping()` assigns BPF registers to PowerPC registers: return value to `r8`, args to `r3`-`r7`, callee-saved BPF registers to `r27`-`r31`, AX to `r12`, temporaries to `r9`/`r10`, and arena VM base to `r26`.
- Stack helpers `bpf_has_stack_frame()`, `bpf_jit_stack_local()`, `bpf_jit_stack_tailcallinfo_offset()`, `bpf_jit_stack_offsetof()`, and `bpf_jit_stack_size()` compute frame/redzone offsets for normal programs, subprograms, tail calls, and exception callbacks.
- `bpf_jit_build_prologue()` saves LR and nonvolatile registers when needed, initializes or propagates tail-call accounting, handles exception-boundary extra saves (`r14`-`r25`), reuses an exception boundary frame for callbacks, configures BPF frame pointer/private stack, and loads `arena_vm_start`.
- `bpf_jit_emit_common_epilogue()` and `bpf_jit_build_epilogue()` restore saved registers, tear down the frame, move BPF return value to ABI return register `r3`, return via `blr`, and append fentry stubs.
- `arch_bpf_stack_walk()` walks PowerPC stack frames for BPF callbacks using `current_stack_frame()` and `validate_sp()`.
- `bpf_jit_emit_func_call_rel()` emits direct helper/kfunc/subprogram calls, handling PC-relative kernels, TOC-relative addressing, module functions, ELF ABI v1 function descriptors, and initial-pass placeholder NOPs.
- `prepare_for_kfunc_call()` uses BTF function model metadata to sign-extend or zero-extend kfunc arguments according to the PowerPC C ABI.
- `bpf_jit_emit_tail_call()` emits bounds checks, tail-call count checks, program lookup from `struct bpf_array`, tail-call counter writeback, common epilogue teardown, and branch through CTR.
- `bpf_jit_bypass_spec_v1()`, `bpf_jit_bypass_spec_v4()`, and `bpf_stf_barrier()` implement JIT-side Spectre/STF mitigation decisions and fallback barrier code.
- `bpf_jit_emit_atomic_ops()` emits LL/SC loops for BPF atomic add/and/or/xor/xchg/cmpxchg and applies full `sync` ordering around fetch operations.
- `emit_atomic_ld_st()` emits acquire loads and release stores with `lwsync`.
- `bpf_jit_build_body()` is the central instruction dispatcher translating BPF ALU, endian, memory, atomic, load, call, branch, exit, tail-call, and probe-memory opcodes into PowerPC instructions.

## Control Flow

JIT compilation first initializes register mapping and runs sizing/codegen passes over the BPF instruction array. Prologue emission decides between redzone use and a real stack frame, then saves only seen nonvolatile registers except where exception handling forces broader saves. The body loop records `addrs[i]` offsets for each BPF instruction, marks seen nonvolatile registers, translates each opcode, and updates address entries for 64-bit immediates and verifier-generated zero-extension insns. Branch translation relies on the populated `addrs` table. Calls mark `SEEN_FUNC`, resolve function targets through BPF core helpers, optionally prepare kfunc arguments, and emit ABI-aware calls. Exits branch to the epilogue unless they are the final instruction. Tail calls bypass normal return by tearing down the current frame and branching to the target program body past its prologue.

## State And Persistence

The file does not persist state outside generated code and the passed `codegen_context`. Important mutable state is in `ctx`: register-use bitmaps, stack size, pass index, exception flags, `arena_vm_start`, user VM base, private stack pointer/size, and `seen` flags. Generated code stores runtime state in the current stack frame or redzone, especially saved nonvolatile registers and `tail_call_info`. Tail-call count is kept in the main program frame and subprogram frames may hold a pointer to that count. Atomic operations use CPU reservation state through `ldarx`/`lwarx` and `stdcx`/`stwcx`.

## Dependencies And Integration Points

This backend depends on Linux BPF core APIs (`struct bpf_prog`, BPF opcode helpers, `bpf_jit_get_func_addr()`, kfunc BTF models, extable support), PowerPC instruction emission macros from `bpf_jit.h`, PACA fields, TOC/kernelbase handling, security feature flags, cache/exception support, and kernel/module text helpers. It integrates with verifier decisions such as `verifier_zext`, kfunc metadata, arena/probe memory exception-table recovery, BPF tail-call arrays, fentry stubs, and architecture BPF stack walking.

## Risks And Edge Cases

High-risk areas are stack offset correctness across redzone, frame, private-stack, and exception-callback modes; ABI correctness for ELF v1/v2 and PC-relative kernels; branch offset calculations across multi-pass JIT emission; tail-call count interpretation as either value or pointer; probe-memory exception-table entries for multi-instruction unaligned loads/stores; arena base restoration; and memory-ordering semantics for atomic fetch operations. Speculation mitigation depends on runtime security features and CPU-specific barrier forms. Unsupported opcodes and unsupported byte/halfword atomics return errors, which must remain aligned with verifier expectations.

## Test Signals

Useful tests include BPF selftests on PowerPC64 for ALU32 zero extension, kfunc signed/unsigned arguments, helper calls from modules and core kernel, BPF-to-BPF calls, tail-call chains and limit enforcement, exception callbacks, arena/probe-memory loads/stores with fault injection, atomic fetch/cmpxchg behavior under SMP, endian conversion, Spectre/STF barrier selection, and branch offset stress programs. Kernel build coverage should include big/little endian, ELF ABI v1/v2, `CONFIG_PPC_KERNEL_PCREL`, Book3S/E500 security feature combinations, and private-stack/exception-boundary configs.
