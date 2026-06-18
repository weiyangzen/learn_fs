# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-loongarch.c

Purpose: Provides LoongArch perf-register to DWARF-register conversion. `__get_dwarf_regnum_for_perf_regnum_loongarch(int perf_regnum)` bounds-checks against `PERF_REG_LOONGARCH_MAX` and returns an identity mapping for valid values.

Control flow and state: Stateless validation-only wrapper; invalid inputs return `-ENOENT`.

Dependencies and integration: Uses LoongArch uapi perf register definitions and is selected by `dwarf-regs.c` for `EM_LOONGARCH`.

Risks: Assumes LoongArch perf and DWARF numbering match. Future uapi additions or libdw frame register limits need coordinated updates.

Test signals: Bounds tests plus representative GPR/PC register mappings on LoongArch perf data.
