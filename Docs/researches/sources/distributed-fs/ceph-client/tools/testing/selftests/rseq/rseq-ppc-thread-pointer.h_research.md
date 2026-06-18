# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc-thread-pointer.h

Purpose: `rseq-ppc-thread-pointer.h` returns the PowerPC thread pointer for locating TLS rseq state.

Important APIs, types, and functions: it exposes `static inline void *rseq_thread_pointer(void)`. On powerpc64 it reads register `r13`; on 32-bit PowerPC it reads register `r2`.

Control flow: there are only compile-time branches for 64-bit versus 32-bit. Runtime behavior is a register move through an empty inline assembly constraint.

State and persistence: no state is stored. The result is used to compute `rseq_offset` and to access `rseq_get_abi()` on each thread.

Dependencies and integration points: selected by `rseq-thread-pointer.h` under `__PPC__`. It integrates with `rseq.c` initialization and all PowerPC rseq helpers.

Risks and test signals: ABI mismatch around TLS register conventions would break all helper access. Successful rseq registration and current CPU reads on PowerPC are the validation signals.
