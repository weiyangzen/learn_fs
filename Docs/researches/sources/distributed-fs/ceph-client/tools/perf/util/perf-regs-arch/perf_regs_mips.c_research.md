
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_mips.c

Purpose: maps MIPS perf register IDs to names and exposes IP/SP IDs.

Important APIs/types/functions: `__perf_reg_mask_mips` returns `PERF_REGS_MASK`. `__perf_reg_name_mips` maps PC and general registers `$1` through `$25`, `$28`, `$29`, `$30`, and `$31`. `__perf_reg_ip_mips` returns PC and `__perf_reg_sp_mips` returns R29.

Control flow: direct switch mapping.

State and persistence: no state.

Dependencies: generic perf regs and MIPS arch register definitions.

Integration points: perf register sampling and display on MIPS.

Risks: missing IDs intentionally reflect architecture definitions; adding kernel registers requires table updates. Test signals include register list output and decoded sampled register names.
