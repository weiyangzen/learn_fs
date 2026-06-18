# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/skip-callchain-idx.c

Purpose: PowerPC callchain cleanup helper that uses DWARF CFI to skip unnecessary LR-derived callchain slots.

Important APIs/types/functions: `check_return_reg`, `check_return_addr`, `arch_skip_callchain_idx`.

Control flow: Finds the DSO/module for a sampled PC, queries `.eh_frame`/`.debug_frame`, determines whether return address is still in LR or on stack, then returns the callchain index to suppress.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libdwfl/libdw, perf thread/map/DSO/callchain structures, and PowerPC ABI register behavior.

Risks: Missing debug info falls back to no skip; incorrect CFI interpretation creates duplicate or missing callgraph arcs.

Test signals: PowerPC perf callgraph tests with leaf, non-leaf, split-debug, and missing-CFI binaries.

Source coverage: researched from the complete local file (258 lines, 6332 bytes).
