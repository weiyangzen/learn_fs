
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_csky.c

Purpose: provides C-SKY register masks, names, and IP/SP register IDs.

Important APIs/types/functions: `__perf_reg_mask_csky` returns `PERF_REGS_MASK`. `__perf_reg_name_csky` maps ABI v2 register IDs to names including a0-a3, regs0-regs9, sp, lr, pc, exregs0-exregs14, tls, hi, and lo, while suppressing extended register names for ABI v2 when the ELF flags indicate they are not valid. `__perf_reg_ip_csky` returns PC and `__perf_reg_sp_csky` returns SP.

Control flow: direct mask return and switch mapping with an ABI/e_flags guard before the switch.

State and persistence: no state.

Dependencies: ELF C-SKY ABI flags, generic perf regs, and C-SKY arch register definitions with ABI v2 definitions forced.

Integration points: register option parsing and sample display for C-SKY perf.

Risks: ABI flag handling is easy to invert; names must reflect the sampled binary ABI. Test signals include ABI-specific register listing/decoding and compile coverage where EF_CSKY constants are absent.
