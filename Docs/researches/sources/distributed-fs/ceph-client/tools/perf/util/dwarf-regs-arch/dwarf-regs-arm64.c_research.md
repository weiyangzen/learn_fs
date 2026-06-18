# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-arm64.c

Purpose: Provides AArch64-specific conversion from perf register numbers to DWARF register numbers. `__get_dwarf_regnum_for_perf_regnum_arm64(int perf_regnum)` checks `0 <= perf_regnum < PERF_REG_ARM64_MAX` and returns the input as the DWARF number when valid.

Control flow and state: Stateless identity mapping with `-ENOENT` for invalid registers.

Dependencies and integration: Depends on `arch/arm64/include/uapi/asm/perf_regs.h` and `dwarf-regs.h`. The generic dispatcher calls it for `EM_AARCH64`.

Risks: Same-number assumption must remain aligned with kernel perf register definitions and libdw AArch64 frame numbering. Register additions beyond libdw support are filtered later by `only_libdw_supported`.

Test signals: Unit coverage for bounds and common x/sp/pc register mappings; end-to-end callchain/register-variable resolution on AArch64.
