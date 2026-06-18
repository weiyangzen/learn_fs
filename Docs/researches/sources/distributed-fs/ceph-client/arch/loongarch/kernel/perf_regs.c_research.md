## sources/distributed-fs/ceph-client/arch/loongarch/kernel/perf_regs.c

### Purpose
`perf_regs.c` implements LoongArch register sampling ABI helpers for perf. It reports whether a task is using 32-bit or 64-bit register ABI, validates requested register masks, and extracts sampled register values from `pt_regs`.

### Important APIs, Types, And Functions
The file defines `perf_reg_abi`, `perf_reg_validate`, `perf_reg_value`, and `perf_get_regs_user`. It uses `PERF_REG_LOONGARCH_MAX`, `PERF_REG_LOONGARCH_PC`, `PERF_SAMPLE_REGS_ABI_32`, `PERF_SAMPLE_REGS_ABI_64`, and thread flag `TIF_32BIT_REGS`.

### Control Flow
ABI selection is compile-time fixed for 32-bit kernels and task-flag dependent for 64-bit kernels. Mask validation rejects empty masks and bits outside the LoongArch perf register range. Value lookup returns `csr_era` for the PC pseudo-register and GPR array entries otherwise. User register capture points perf at `task_pt_regs(current)`.

### State, Persistence, And Dependencies
No local state persists. It depends on stable `pt_regs` layout, LoongArch perf register enum definitions, and thread flags set by ABI/personality code.

### Integration Points
`perf_event_open` register sampling and sample formatting call these helpers. `perf_event.c` callchain and PMU support complement this file for complete perf samples.

### Risks
Register enum order must match `pt_regs->regs[]`; otherwise sampled register masks return wrong registers. `perf_get_regs_user` always samples current task registers, which is correct for perf user samples but would be wrong if reused for arbitrary tasks.

### Test Signals
Use `perf record --sample-regs` with GPR and PC masks on 32-bit and 64-bit tasks. Validate rejected masks and compare sampled PC/registers against ptrace or signal-frame register dumps.
