# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_invalid.c

Purpose: compact negative matrix proving every supported atomic opcode form rejects when the destination is a scalar rather than a pointer.

Important APIs/types/functions: defines `__INVALID_ATOMIC_ACCESS_TEST(op)`, which emits `BPF_ATOMIC_OP(BPF_DW, op, BPF_REG_1, BPF_REG_0, -8)` after making `R1` a scalar zero. It instantiates add, fetch-add, and, fetch-and, or, fetch-or, xor, fetch-xor, xchg, and cmpxchg variants.

Control flow: each generated test sets `R0 = 1`, `R1 = 0`, performs an atomic operation through `R1 - 8`, then would exit if accepted. The verifier should reject before runtime.

State and persistence behavior: no persistent state; the only relevant state is verifier register typing. `R1` must remain scalar and cannot be converted to a memory pointer by atomic addressing syntax.

Dependencies and integration points: included by the verifier test harness; all outcomes are `.result = REJECT` with the same diagnostic.

Risks: if any new atomic opcode is added without this scalar-pointer rejection coverage, invalid memory access could slip through. The duplicate add instantiations also make exact macro edits easy to disturb.

Test signals: every case rejects with `R1 invalid mem access 'scalar'`.
