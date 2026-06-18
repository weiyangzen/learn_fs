<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_regs.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_regs.c

### Purpose
`perf_regs.c` exposes PA-RISC register snapshots to the generic perf sampled-registers API.

### Important APIs, Types, And Functions
`perf_reg_value()` maps `PERF_REG_PARISC_*` indexes to fields in `struct pt_regs`. `perf_reg_validate()` rejects empty masks and masks with bits above `PERF_REG_PARISC_MAX`. `perf_reg_abi()` reports 32-bit or 64-bit ABI based on kernel width and `TIF_32BIT`. `perf_get_regs_user()` fills `struct perf_regs` for the current task.

### Control Flow
Perf asks for a register value by index; the switch reads general, space, instruction queue, and control-derived trap registers. ABI selection is purely conditional. User register collection ignores the passed `regs` argument and uses `task_pt_regs(current)`.

### State, Persistence, And Dependencies
No state is persisted. The code depends on `asm/ptrace.h`, perf register enumerations, task thread flags, and the correctness of `struct pt_regs` layout.

### Integration Points
Used by perf sampling and unwinding when user register masks are requested.

### Risks
The `PERF_REG_PARISC_IAOQ*` case reads `regs->iasq[]`, which appears inconsistent with the index name and could report space queue values instead of instruction offsets. ABI reporting must match compat task handling or user tools decode registers incorrectly.

### Test Signals
Perf tests should sample GPRs, SRs, IASQ/IAOQ, and SAR/IIR/ISR/IOR/IPSW on 32-bit, 64-bit, and compat tasks, and should validate bad masks return `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_regs.c -->
