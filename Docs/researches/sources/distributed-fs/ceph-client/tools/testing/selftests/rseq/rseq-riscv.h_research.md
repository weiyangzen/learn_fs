# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq-riscv.h

Purpose: `rseq-riscv.h` defines the RISC-V architecture-specific rseq layer.

Important APIs, types, and functions: it selects `RSEQ_SIG`, enforces little-endian builds, picks `ld/sd` versus `lw/sw` through `__riscv_xlen`, defines `RISCV_FENCE`-based memory barriers, acquire/release helpers, table/exit/abort macros, CPU compare, load/store/add snippets, byte-copy helper, and offset-deref-add operation.

Control flow: it expands `rseq-riscv-bits.h` for CPU-id relaxed/release, mm-cid relaxed/release, and CPU-id-none relaxed variants.

State and persistence: it defines descriptor and active-CS publication behavior but owns no runtime state directly. Generated helpers update TLS and caller memory according to rseq semantics.

Dependencies and integration points: selected by `rseq.h` on `__riscv`. It depends on `<asm/fence.h>`, endian definitions, and RISC-V assembler syntax. It integrates with `param_test.c` and membarrier coverage.

Risks and test signals: the signature uses an uncommon privileged CSR instruction instead of `ebreak`, making exact encoding important. Register-width and endian constraints are key. Passing RISC-V CPU-id/mm-cid tests and membarrier restart tests validate this layer.
