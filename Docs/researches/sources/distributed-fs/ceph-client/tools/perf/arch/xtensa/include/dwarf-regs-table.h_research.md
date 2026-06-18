# Research: sources/distributed-fs/ceph-client/tools/perf/arch/xtensa/include/dwarf-regs-table.h

Purpose: supplies the Xtensa perf DWARF register name table.

Important APIs/types/functions: defines `REG_DWARFNUM_NAME(r, num)` entries for `a0` through `a15` mapped to DWARF register numbers 0 through 15.

Control flow: header data only; consumed by generic register table generation logic.

State and persistence: no runtime state.

Dependencies and integration: depends on the includer defining `REG_DWARFNUM_NAME`. Integrated into perf's architecture-specific DWARF register lookup.

Risks: minimal but ABI-sensitive; missing special registers means only the listed general address registers are named.

Test signals: Xtensa perf build and `perf probe`/DWARF register name lookup tests.
