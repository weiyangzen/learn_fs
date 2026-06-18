# sources/distributed-fs/ceph-client/arch/powerpc/perf/perf_regs.c

Purpose: implements PowerPC perf sampled-register support, mapping perf register IDs to `pt_regs` offsets or PMU SPR reads and validating user-requested register masks.

Important APIs/types/functions: global `PERF_REG_EXTENDED_MASK`, `pt_regs_offset`, `get_ext_regs_value`, `perf_reg_value`, `perf_reg_validate`, `perf_reg_abi`, and `perf_get_regs_user`.

Control flow and state: normal register IDs read from `pt_regs` by offset. Extended PMU IDs read live SPRs or helper `get_pmcs_ext_regs`. SIER/MMCRA return zero when unsupported by config or platform. Validation rejects empty masks and masks outside `PERF_REG_EXTENDED_MASK | PERF_REG_PMU_MASK`. ABI selection checks whether the target task is 32-bit.

State and persistence behavior: no persistent state. `PERF_REG_EXTENDED_MASK` is a global capability mask set by PMU init code such as POWER10/11 setup. Register reads are snapshots from interrupt/user contexts or current SPR state.

Dependencies and integration points: used by perf sample register collection. Depends on `asm/perf_regs.h`, `pt_regs`, PowerPC SPR access, PMU-specific extended mask setup, `is_sier_available`, `get_pmcs_ext_regs`, and task ABI helpers.

Risks: extended SPR reads may be invalid on CPUs unless the mask is set correctly; SIER and MMCRA reuse `pt_regs` `dar`/`dsisr` storage in interrupt paths, so producer and consumer must agree; user register capture ignores the provided `regs` argument and uses `task_pt_regs(current)`.

Test signals: perf record with `--sample-regs` on 32-bit and 64-bit tasks, PMU extended register sampling on POWER10, SIER-disabled systems returning zero, invalid mask rejection, and ABI values matching task mode.
