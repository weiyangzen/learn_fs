# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-x86-bits.h

Purpose: `rseq-x86-bits.h` implements the generated x86 restartable-sequence primitives for both x86-64 and i386.

Important APIs, types, and functions: for x86-64 it generates `rseq_cmpeqv_storev`, `rseq_cmpnev_storeoffp_load`, `rseq_addv`, `rseq_offset_deref_addv`, `rseq_cmpeqv_cmpeqv_storev`, `rseq_cmpeqv_trystorev_storev`, and `rseq_cmpeqv_trymemcpy_storev`. For i386 it generates the same common set except offset-deref-add is not present in the scanned lower half. `RSEQ_ARCH_HAS_OFFSET_DEREF_ADDV` is defined for x86-64, enabling membarrier tests.

Control flow: each helper uses `asm goto`, stores `rseq_cs`, compares the ABI CPU/mm-cid field through the FS or GS TLS segment, performs operation-specific checks and writes, and exits through success, cmpfail, or abort labels. Optional `RSEQ_COMPARE_TWICE` adds duplicate validation labels to catch compiler/kernel consistency problems.

State and persistence: the helpers modify TLS `rseq_cs` and caller-provided memory. They use active CS descriptors emitted into `__rseq_cs` and pointer arrays for kernel and debugger consumption.

Dependencies and integration points: depends on `rseq-x86.h` for signatures, segment selectors, memory barriers, table layout, and abort/cmpfail macros. Called through wrappers in `rseq.h` by `param_test.c`.

Risks and test signals: x86 inline asm has separate 32-bit and 64-bit paths, with known compiler constraints around TLS memory operands. The memcpy helper copies bytewise within a critical section and must keep final store placement exact. Passing x86 default, compare-twice, mm-cid, release, and membarrier tests are the primary signals.
