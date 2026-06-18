# sources/distributed-fs/ceph-client/tools/perf/arch/arm/tests/dwarf-unwind.c

Purpose: Creates architecture-specific synthetic unwind samples for perf tests.

Important APIs/types/functions: `sample_ustack`, `test__arch_unwind_sample`, `STACK_SIZE`.

Control flow: Populates sampled user registers and stack bytes from `perf_regs_load()`/assembly helpers, maps the test function, and invokes common unwind validation.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind support, perf sample structures, map/thread helpers, and architecture register layout.

Risks: Stack pointer/register index mismatches produce fragile test-only failures or mask real unwinder regressions.

Test signals: Run the architecture DWARF unwind perf test under frame-pointer and DWARF unwind configurations.

Source coverage: researched from the complete local file (64 lines, 1371 bytes).
