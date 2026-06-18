# sources/distributed-fs/ceph-client/tools/perf/arch/riscv/include/perf_regs.h

Purpose: Defines riscv perf sample register masks, ABI selection, and optional `perf_regs_load()` declaration.

Important APIs/types/functions: `ARCH_PERF_REGS_H`, `PERF_REGS_MASK`, `PERF_REGS_MAX`, `PERF_SAMPLE_REGS_ABI`.

Control flow: Perf uses the mask and ABI macros when requesting or decoding sampled user registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on kernel `perf_event.h` architecture register enums and word-size config.

Risks: Mask/ABI mismatches cause unsupported register requests or incorrectly decoded samples.

Test signals: Build riscv perf and run register sampling/unwind tests for supported ABIs.

Source coverage: researched from the complete local file (25 lines, 625 bytes).
