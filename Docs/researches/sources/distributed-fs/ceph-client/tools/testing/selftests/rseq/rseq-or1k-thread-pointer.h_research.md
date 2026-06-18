# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-or1k-thread-pointer.h

Purpose: `rseq-or1k-thread-pointer.h` implements thread-pointer retrieval for OpenRISC.

Important APIs, types, and functions: it exposes `static inline void *rseq_thread_pointer(void)`, implemented by copying OR1K register `r10` into a C pointer through inline assembly.

Control flow: the function has no branches. Header guards prevent duplicate definition.

State and persistence: no state is stored. The returned thread pointer is used by `rseq.c` and `rseq.h` to locate the current thread's rseq ABI area.

Dependencies and integration points: selected by `rseq-thread-pointer.h` when `__or1k__` is defined. It integrates with the self-owned TLS registration path in `rseq.c`.

Risks and test signals: the risk is ABI dependence on `r10` as the thread register. Incorrect register selection would make `rseq_get_abi()` point at invalid TLS. Registration success and correct CPU/mm-cid reads are the practical test signals.
