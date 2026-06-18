# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-mips.c

Purpose: Provides MIPS perf-register to DWARF-register conversion with special handling for PC. `__get_dwarf_regnum_for_perf_regnum_mips(int perf_regnum)` maps `PERF_REG_MIPS_PC` to DWARF register 37, validates other values against `PERF_REG_MIPS_MAX`, and otherwise uses identity mapping.

Control flow and state: Stateless branch for PC followed by bounds check.

Dependencies and integration: Uses MIPS uapi perf register definitions and is called by the generic dispatcher for `EM_MIPS`.

Risks: The explicit PC mapping must stay aligned with MIPS DWARF conventions. Other registers rely on identity numbering, so uapi reordering or additions are potential integration risks.

Test signals: Tests for PC, negative/out-of-range values, and several GPR/FPR mappings; regression tests on MIPS perf samples with instruction pointer register dumps.
