# sources/distributed-fs/ceph-client/arch/x86/net/bpf_timed_may_goto.S

## Purpose
Provides the x86-64 assembly thunk `arch_bpf_timed_may_goto`, used by the BPF JIT timed may-goto feature. It preserves BPF caller-visible registers, calls the C helper `bpf_check_timed_may_goto()`, and returns the helper result in BPF temporary register `r10`/`BPF_REG_AX`.

## Important APIs, types, and functions
- `SYM_FUNC_START(arch_bpf_timed_may_goto)` defines the exported assembly entry.
- `ANNOTATE_NOENDBR` marks the function as not requiring an ENDBR landing pad.
- `CALL_DEPTH_ACCOUNT` emits x86 call-depth mitigation accounting before the helper call.
- The external integration point is `bpf_check_timed_may_goto`.

## Control flow
The caller passes stack depth in `r10`. The thunk computes a pointer to the count/timestamp storage by adding `r10` to BPF frame pointer `rbp`. It creates a normal frame, saves BPF R0-R5 physical registers (`rax`, `rdi`, `rsi`, `rdx`, `rcx`, `r8`), moves the count/timestamp pointer into `rdi`, performs call-depth accounting, and calls `bpf_check_timed_may_goto`. The return value in `rax` is moved to `r10`, saved registers are restored, and the function returns through the mitigation-aware `RET` macro.

## State and persistence
The only state touched is the caller stack slot referenced through `rbp + stack_depth`, as consumed by `bpf_check_timed_may_goto`. The assembly preserves BPF-visible argument/result registers except for the intended result in `r10`.

## Dependencies and integration points
This file depends on x86-64 mode, Linux linkage macros, export/linkage infrastructure, and x86 nospec branch macros. It is enabled by the x86-64 JIT feature hook `bpf_jit_supports_timed_may_goto()` in `bpf_jit_comp.c`.

## Risks and edge cases
The register-save set must match the JIT ABI. A wrong stack-depth convention would pass the helper an invalid count/timestamp pointer. Missing call-depth accounting or an incorrect return macro could violate x86 mitigation expectations. The thunk is 64-bit only and assumes a BPF frame pointer in `rbp`.

## Test signals
BPF timed may-goto selftests should confirm counter/timestamp updates and register preservation across the helper call. Kernel objtool/linkage checks should validate annotations and return behavior.
