# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_xchg.c

Purpose: smoke-tests atomic exchange for 64-bit and 32-bit stack slots.

Important APIs/types/functions: uses `BPF_ATOMIC_OP` with `BPF_XCHG`, stack stores, loads, and 64-bit or 32-bit conditional jumps.

Control flow: each case initializes a stack slot to `3`, exchanges in `4` through `R1`, checks that `R1` receives old value `3`, then loads memory to confirm it is now `4`.

State and persistence behavior: only stack and register state is involved. The important property is that xchg always fetches the old value into the source register, unlike non-fetch bitwise atomic ops.

Dependencies and integration points: harness-only test fragment, no helper or map fixups.

Risks: incorrect JIT lowering could either fail to store the new value or fail to return the old value. 32-bit comparisons must use `BPF_JMP32_IMM`.

Test signals: both tests expect `ACCEPT`; nonzero runtime exits identify old-value or final-memory mismatches.
