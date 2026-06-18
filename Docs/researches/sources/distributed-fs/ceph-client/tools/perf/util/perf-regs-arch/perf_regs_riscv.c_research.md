
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_riscv.c

Purpose: maps RISC-V perf register IDs to ABI register names and exposes masks/IP/SP IDs.

Important APIs/types/functions: `__perf_reg_mask_riscv` returns `PERF_REGS_MASK`. `__perf_reg_name_riscv` maps pc, ra, sp, gp, tp, t0-t6, s0-s11, and a0-a7. `__perf_reg_ip_riscv` returns PC and `__perf_reg_sp_riscv` returns SP.

Control flow: direct switch mapping.

State and persistence: no state.

Dependencies: generic perf regs and RISC-V arch register definitions.

Integration points: perf register option parsing and sample register display on RISC-V.

Risks: ABI aliases are user-facing and should stay consistent with docs. Test signals include `--user-regs=?` and decoded register samples.
