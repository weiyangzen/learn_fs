# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-riscv.c

Purpose: Provides RISC-V perf-register to DWARF-register conversion. `__get_dwarf_regnum_for_perf_regnum_riscv(int perf_regnum)` returns the same number for registers in `[0, PERF_REG_RISCV_MAX)`, otherwise `-ENOENT`.

Control flow and state: Stateless bounds-checked identity mapping.

Dependencies and integration: Depends on RISC-V uapi perf register definitions and the generic `dwarf-regs.h` contract. Used for `EM_RISCV`.

Risks: Assumes kernel perf register numbering matches DWARF numbering. Libdw support filtering in the generic layer should catch registers beyond known frame ranges.

Test signals: Bounds tests and representative integer/floating register translation on RISC-V data.
