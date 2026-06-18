# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_tailcall_jit.c

## Purpose
`verifier_tailcall_jit.c` validates x86-64 JIT code generation around tail calls from subprograms. It checks the prologue and tail-call counter storage/restoration sequences needed when a BPF program calls a subprogram that performs `bpf_tail_call`.

## Important APIs, Types, and Functions
The file defines a `BPF_MAP_TYPE_PROG_ARRAY` named `jmp_table` with entry 0 pointing back to `main`. A static auxiliary naked function `sub` loads the prog array and key then calls helper number 12, `bpf_tail_call`. The `main` TC program calls `sub`, returns zero, and is annotated with `__arch_x86_64` plus many `__jited` expected assembly fragments.

## Control Flow
At BPF level, `main` calls `sub`; `sub` attempts a tail call to `main`; if tail-call limits prevent transfer, it exits. At JIT level, the test expects the entry program to establish a tail-call counter on the stack, pass or restore the counter pointer in `rax`, and for the subprogram to increment the shared counter before jumping to the target.

## State and Persistence
Persistent state is the prog-array map binding `main` as a tail-call target. Runtime state is the JIT-managed tail-call counter stored on the native stack and passed through `rax`. No external persistence exists.

## Dependencies and Integration Points
The test is x86-64 specific and depends on the selftest runner's JIT disassembly matcher. It integrates with TC program loading, prog-array tail calls, subprogram calls, and x86 retpoline/rethunk tolerant return matching.

## Risks and Test Signals
Risks include tail-call counter corruption, unbounded recursive tail calls, or subprogram prologues failing to preserve counter pointers across calls. Test signals are exact native assembly fragments: stack slots at `rbp[-8]` and `rbp[-16]`, compare against 33, increment of `*tail_call_cnt_ptr`, and a final jump to the tail-call target.
