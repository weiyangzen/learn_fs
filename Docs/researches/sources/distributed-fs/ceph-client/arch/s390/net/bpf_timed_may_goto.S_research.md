## sources/distributed-fs/ceph-client/arch/s390/net/bpf_timed_may_goto.S

Purpose: provides the s390 assembly helper `arch_bpf_timed_may_goto` used by the BPF JIT for timed conditional looping support.

Important APIs, types, and functions: `SYM_FUNC_START(arch_bpf_timed_may_goto)` defines a special-ABI function. It calls `bpf_check_timed_may_goto`. It also emits an indirect branch thunk with `GEN_BR_THUNK %r1` and returns using `BR_EX`.

Control flow: the helper receives parameters in `%r12` and `%r13`, return address in `%r0`, and preserves all GPRs except `%r0`, `%r1`, and `%r12`. It saves `%r2`-`%r5`, `%r14`, the return address, `%r15`, and backchain in a compact frame, computes `%r2 = %r12 + %r13`, calls `bpf_check_timed_may_goto`, moves `%r2` back to `%r12`, restores saved registers, loads return address into `%r1`, and branches through the nospec-aware return macro.

State and persistence: no global state. It uses stack frame state only for register preservation and backchain.

Dependencies and integration points: depends on s390 stack frame offsets from `asm-offsets.h`, nospec branch macros, BPF core `bpf_check_timed_may_goto`, and the JIT special-case call path that expects this ABI.

Risks: stack-frame offset math is guarded by a preprocessor check, but ABI drift between the JIT and this helper would corrupt BPF registers or return address. The special clobber set must remain synchronized with `bpf_jit_comp.c`.

Test signals: BPF timed may-goto selftests, register preservation checks across helper calls, stack unwinding/backchain validation, and nospec thunk build coverage.
