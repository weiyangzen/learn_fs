# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-ppc.h

Purpose: `rseq-ppc.h` is the PowerPC architecture definition layer for rseq selftest helpers.

Important APIs, types, and functions: it defines the PowerPC trap signature `RSEQ_SIG`, `sync`/`lwsync` barriers, acquire/release helpers, 32-bit versus 64-bit load/store instruction macros, `RSEQ_ASM_DEFINE_TABLE()`, `RSEQ_ASM_DEFINE_EXIT_POINT()`, `RSEQ_ASM_STORE_RSEQ_CS()`, `RSEQ_ASM_CMP_CPU_ID()`, `RSEQ_ASM_DEFINE_ABORT()`, compare/store/load/add snippets, and a byte-copy helper.

Control flow: after selecting 32-bit or 64-bit instruction forms, it includes `rseq-ppc-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed helpers.

State and persistence: no standalone runtime state is owned here. It defines how descriptors are emitted into ELF sections and how generated helpers store `rseq_cs` in TLS and commit caller memory.

Dependencies and integration points: selected by `rseq.h` for `__PPC__`. It depends on PowerPC ABI register and endian assumptions, and its generated helpers are used by the parameter test suite.

Risks and test signals: risks include 32-bit versus 64-bit table layout, PC-relative address construction, and memory-order semantics. Test signals are successful PowerPC builds and passing selftests across CPU-id/mm-cid and relaxed/release variants.
