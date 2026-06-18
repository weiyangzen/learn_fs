# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_cmpxchg.c

Purpose: exercises verifier and runtime semantics for `BPF_ATOMIC_OP(..., BPF_CMPXCHG, ...)` on stack memory, including 64-bit and 32-bit compare-exchange success and failure paths, returned old values, and post-operation memory contents.

Important APIs/types/functions: uses verifier-test macros `BPF_ST_MEM`, `BPF_MOV64_IMM`, `BPF_MOV32_IMM`, `BPF_ATOMIC_OP`, `BPF_LDX_MEM`, `BPF_JMP_IMM`, `BPF_JMP32_IMM`, and `BPF_EXIT_INSN`. The tests rely on `BPF_DW`, `BPF_W`, `BPF_CMPXCHG`, `BPF_REG_10` as frame pointer, and special treatment of `BPF_REG_0` as both compare input and returned old value.

Control flow: the smoke tests initialize a stack slot to `3`, attempt a non-matching compare-exchange, assert that the old value and memory remain `3`, then attempt a matching exchange to `4`. Later cases drive verifier rejection or privileged/unprivileged divergence by placing stack or frame-pointer-derived pointers in `R0`, copying only 32 bits of pointers, and loading through the cmpxchg return value.

State and persistence behavior: all mutable state is transient verifier test state in registers and stack slots. The file specifically checks verifier register state after cmpxchg: `BPF_W` cmpxchg must zero the upper 32 bits of `R0`, pointer-typed returned values may remain usable for privileged programs, and unprivileged mode must reject pointer leaks into memory.

Dependencies and integration points: integrated by inclusion into the BPF verifier test harness, which interprets `.insns`, `.result`, `.result_unpriv`, `.errstr`, `.errstr_unpriv`, and `.flags`. No standalone functions are exported.

Risks: changes to atomic return typing, 32-bit zero-extension, or pointer-leak diagnostics can silently weaken verifier guarantees. The `F_NEEDS_EFFICIENT_UNALIGNED_ACCESS` case is architecture-sensitive and should be preserved when adjusting expected failures.

Test signals: expected outcomes include `ACCEPT`, `REJECT`, unprivileged rejection with `R0 leaks addr into mem` or `R10 partial copy of pointer`, normal rejection with `invalid size of register fill` or `R0 invalid mem access`, and successful 32-bit zero-extension.
