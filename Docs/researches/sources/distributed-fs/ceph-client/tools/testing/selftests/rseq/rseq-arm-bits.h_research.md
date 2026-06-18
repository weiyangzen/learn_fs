# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-arm-bits.h

Purpose: `rseq-arm-bits.h` instantiates ARM 32-bit rseq critical sections through the common template mechanism. It is included multiple times by `rseq-arm.h` to produce CPU-id, mm-cid, relaxed, release, and CPU-id-independent helper names.

Important APIs, types, and functions: it defines always-inline implementations for `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`, each renamed by `RSEQ_TEMPLATE_IDENTIFIER()`. These functions map directly to the generic wrappers in `rseq.h`.

Control flow: each function builds an `asm goto` critical section. The sequence stores the active `rseq_cs`, compares the current CPU/mm-cid field with the caller-provided value, performs one or more data checks or speculative stores, reaches the post-commit label on success, or branches to comparison-failure and abort labels. The abort paths call `RSEQ_INJECT_FAILED` and return a negative value, while comparison failures return a positive value.

State and persistence: it updates only caller-provided memory locations and the thread-local active `rseq_cs` pointer. It relies on the kernel to redirect execution to the abort IP when preemption, signal delivery, or migration invalidates the sequence. Release variants insert the ARM memory-ordering operation before the final commit store.

Dependencies and integration points: it depends on macros from `rseq-arm.h` for table emission, abort signatures, CPU comparison, and memory-order operations, plus `rseq-bits-template.h` for suffix selection. It is exercised by `param_test.c` operations on ARM little-endian builds.

Risks and test signals: inline assembly register constraints, Thumb/A32 signature handling, and exact label/table placement are fragile. The header intentionally has no standalone include guard because repeated inclusion is the generation mechanism. Test signals are successful `param_test` runs, especially injected aborts and release-mode buffer/memcpy tests.
