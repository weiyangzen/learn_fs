
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_loongarch.c

Purpose: maps LoongArch perf register IDs to user-facing names and basic masks.

Important APIs/types/functions: `__perf_reg_mask_loongarch` returns `PERF_REGS_MASK`. `__perf_reg_name_loongarch` maps PC and `%r1` through `%r31`. `__perf_reg_ip_loongarch` returns PC and `__perf_reg_sp_loongarch` returns R3.

Control flow: direct switch mapping only.

State and persistence: no state.

Dependencies: generic perf regs and LoongArch arch register definitions.

Integration points: register sampling option parsing and sample display on LoongArch.

Risks: `%rN` casing/prefix is user-visible; SP must stay aligned with the LoongArch ABI. Test signals include register list output and sample decoding tests.
