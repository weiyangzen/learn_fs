
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_arm.c

Purpose: maps 32-bit ARM perf register IDs to names and basic sampling masks.

Important APIs/types/functions: `__perf_reg_mask_arm` returns `PERF_REGS_MASK`. `__perf_reg_name_arm` maps r0-r10, fp, ip, sp, lr, and pc. `__perf_reg_ip_arm` returns PC and `__perf_reg_sp_arm` returns SP.

Control flow: direct switch-based mapping only.

State and persistence: no state.

Dependencies: generic perf regs abstraction and ARM arch register definitions.

Integration points: register sampling options and sample display on ARM builds.

Risks: names must match user-facing register option expectations and kernel register IDs. Test signals include `--user-regs=?` listing and sample register decoding on ARM.
