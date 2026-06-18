# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/tests/regs_load.S

Purpose: Assembly helper that stores live architecture registers into the array expected by perf unwind tests.

Important APIs/types/functions: `STR_REG`, `LDR_REG`, `SP`, `PC`.

Control flow: Defines register offsets and emits stores for general-purpose registers plus PC/LR/SP-style state.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on assembler syntax, calling convention, and `perf_regs.h` ordering.

Risks: Offset drift corrupts synthetic unwind samples.

Test signals: Perf architecture unwind test and objdump review of stored registers.

Source coverage: researched from the complete local file (48 lines, 747 bytes).
