# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_irq.h

### Purpose
`intel_gt_pm_irq.h` declares GT PM interrupt mask, enable, disable, and reset helpers.

### Important APIs, Types, And Functions
It declares `gen6_gt_pm_unmask_irq()`, `gen6_gt_pm_mask_irq()`, `gen6_gt_pm_enable_irq()`, `gen6_gt_pm_disable_irq()`, and `gen6_gt_pm_reset_iir()`.

### Control Flow
RPS/PM code includes this header to update PM IRQ state while holding the GT IRQ lock.

### State, Persistence, And Dependencies
The header stores no state and only forward-declares `struct intel_gt`.

### Integration Points
Used by RPS and interrupt setup paths to control PM interrupt delivery.

### Risks
The API name is Gen6-prefixed but covers later generations via implementation-specific register selection; callers must still respect lock requirements.

### Test Signals
Build coverage and PM IRQ behavior on Gen6+ platforms validate this header.
