# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm.h

Purpose: common HTM capability and failure-code helper header for powerpc transactional-memory selftests.

Important APIs/types/functions: `have_htm()`, `have_htm_nosc()`, `htm_is_synthetic()`, `failure_code()`, `failure_is_persistent()`, `failure_is_syscall()`, `failure_is_unavailable()`, `failure_is_reschedule()`, `failure_is_nesting()`, `tcheck()`, and `tcheck_*()` predicates.

Control flow: capability helpers query HWCAP2 bits. `htm_is_synthetic()` attempts `tbegin./tend.` up to `TM_RETRIES` and classifies Power10 synthetic TM by persistent implementation-specific failures. Failure helpers decode TEXASRU bits and `tcheck` condition result.

State and persistence behavior: stateless inline functions. They read CPU SPR/builtin state from the current thread.

Dependencies and integration points: includes `<asm/tm.h>`, `utils.h`, and `reg.h`, and is widely included by ptrace, signal, and TM tests.

Risks and test signals: synthetic detection is heuristic by necessity and loops to reduce false classification. Missing HWCAP definitions cause printed messages and false capability.
