# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.c

### Purpose
`intel_gt_pm_irq.c` manages GT PM/RPS interrupt enable and mask state for Gen6+ interrupt layouts.

### Important APIs, Types, And Functions
It implements `gen6_gt_pm_unmask_irq()`, `gen6_gt_pm_mask_irq()`, `gen6_gt_pm_enable_irq()`, `gen6_gt_pm_disable_irq()`, and `gen6_gt_pm_reset_iir()`. Internal helpers are `write_pm_imr()`, `write_pm_ier()`, and `gen6_gt_pm_update_irq()`.

### Control Flow
Callers hold `gt->irq_lock`, then enable/disable or mask/unmask PM bits in `gt->pm_ier` and `gt->pm_imr`. Register selection depends on generation: Gen11 uses upper-half WGBOXPERF registers, Gen8 uses `GEN8_GT_*R(2)`, and older Gen6 uses `GEN6_PM*`. Reset writes the IIR twice and posting-reads it.

### State, Persistence, And Dependencies
Persistent state is `gt->pm_ier` and `gt->pm_imr`. Dependencies include GT interrupt locking, uncore MMIO writes, platform version checks, and GT PM register definitions.

### Integration Points
RPS and GT IRQ setup use this file to enable or suppress PM events without disturbing engine interrupts.

### Risks
All functions require `gt->irq_lock`; missing it risks races with IRQ handlers or postinstall/reset. Gen11 bit shifting must match hardware upper-half placement.

### Test Signals
RPS interrupt enable/disable, PM IIR reset behavior, lockdep coverage, and register programming checks on Gen6, Gen8, and Gen11+ platforms are useful.
