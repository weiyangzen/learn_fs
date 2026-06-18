# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-thread-pointer.h

Purpose: `rseq-thread-pointer.h` dispatches to the architecture-specific implementation of `rseq_thread_pointer()`.

Important APIs, types, and functions: it does not define a function itself; it includes `rseq-x86-thread-pointer.h`, `rseq-ppc-thread-pointer.h`, `rseq-or1k-thread-pointer.h`, or `rseq-generic-thread-pointer.h` based on target macros.

Control flow: compile-time selection chooses the appropriate include. Runtime behavior is supplied by the selected header.

State and persistence: no runtime state. The chosen thread-pointer function is foundational for computing and using `rseq_offset`.

Dependencies and integration points: included by `rseq.h` before `rseq_get_abi()` is defined. It is used by `rseq.c` constructor logic to either compute a self-owned TLS offset or use libc-provided offset symbols.

Risks and test signals: wrong architecture dispatch causes invalid TLS access. Test signals include successful compilation on each supported architecture and successful registration/current CPU tests.
