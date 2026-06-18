# sources/distributed-fs/ceph-client/arch/arm64/kernel/perf_regs.c

Purpose: Provides arm64 perf register sampling ABI support for native, compat, and SVE vector-granule registers.

Important APIs: `perf_reg_value()`, `perf_reg_validate()`, `perf_reg_abi()`, and `perf_get_regs_user()`. `perf_ext_regs_value()` currently supports `PERF_REG_ARM64_VG` when SVE exists.

Control flow: register reads validate the index, handle compat mode specially for SP/LR/PC ABI compatibility, return native SP/PC or general regs, and dispatch extended registers. Validation rejects empty masks and reserved bits, except VG when SVE is supported. ABI selection returns 32-bit for compat threads and 64-bit otherwise.

Dependencies and integration: depends on perf event ABI definitions, `pt_regs`, compat task state, SVE vector length state from `fpsimd.c`, and task stack helpers.

Risks and test signals: risks are ABI compatibility regressions for 32-bit tasks sampled by 64-bit tools, exposing unsupported extended regs, and wrong VG values after vector length changes. Test with perf register sampling for native and compat tasks, SVE-enabled systems, invalid masks, and unwinder consumers.
