# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-arm.c

Purpose: Provides ARM-specific conversion from perf register numbers to DWARF register numbers. `__get_dwarf_regnum_for_perf_regnum_arm(int perf_regnum)` validates the input against `PERF_REG_ARM_MAX` from the ARM uapi perf register header and returns the same number for valid registers, or `-ENOENT` for invalid inputs.

Control flow and state: Stateless, single bounds check then identity mapping. No allocation or persistence.

Dependencies and integration: Included by the generic DWARF register dispatcher through declarations in `dwarf-regs.h`; used by `get_dwarf_regnum_for_perf_regnum` when `e_machine` is `EM_ARM`.

Risks: Assumes ARM perf register numbering matches DWARF numbering. If kernel uapi adds non-DWARF or reordered registers, this identity mapping must be revisited.

Test signals: Validate negative, `PERF_REG_ARM_MAX`, and common ARM GPR inputs; integration tests should verify perf sample register decoding on ARM.
