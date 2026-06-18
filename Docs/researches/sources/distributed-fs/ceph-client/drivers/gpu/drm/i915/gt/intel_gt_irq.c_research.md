# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.c

### Purpose
`intel_gt_irq.c` implements GT interrupt dispatch, reset, and postinstall programming for Gen5/6, Gen8, and Gen11+ interrupt layouts, including engine interrupts, PM/RPS interrupts, GuC/GSC/PXP events, media GT routing, and parity errors.

### Important APIs, Types, And Functions
Public functions include `gen11_gt_irq_handler()`, `gen11_gt_irq_reset()`, `gen11_gt_irq_postinstall()`, `gen11_gt_reset_one_iir()`, `gen8_gt_irq_handler()`, `gen8_gt_irq_reset()`, `gen8_gt_irq_postinstall()`, `gen6_gt_irq_handler()`, `gen5_gt_irq_handler()`, `gen5_gt_irq_reset()`, `gen5_gt_irq_postinstall()`, `gen5_gt_enable_irq()`, and `gen5_gt_disable_irq()`. Important internals include `guc_irq_handler()`, `gen11_gt_engine_identity()`, `gen11_gt_identity_handler()`, `pick_gt()`, `gen11_other_irq_handler()`, and parity error handling.

### Control Flow
Gen11+ handlers lock `gt->irq_lock`, scan interrupt banks from the master control value, select an identity register for each set bit, decode engine class/instance/interrupt bits, route media/video/GSC cases to the appropriate GT, and call engine or subsystem handlers before clearing the bank bit. Reset functions disable and mask engine, GuC, GSC, PM, and CCS interrupt registers. Postinstall enables class interrupts and unmasks only supported engine lanes and firmware events. Older generations read generation-specific IIR registers and dispatch to fixed engine class slots.

### State, Persistence, And Dependencies
The file updates `gt->gt_imr`, `gt->pm_ier`, and `gt->pm_imr`, and reads engine class maps, UC interrupt enable state, media GT pointers, and platform feature bits. Dependencies include raw uncore MMIO, i915 IRQ helpers, engine IRQ callbacks, RPS handlers, GuC host events, GSC proxy, PXP, GMD interrupt register definitions, and GT register definitions.

### Integration Points
Top-level display/device IRQ handlers call these generation-specific GT handlers. Engine breadcrumb signaling, GuC submission, RPS frequency control, PXP, GSC firmware, and media GT all receive events through this layer.

### Risks
Interrupt ordering is strict: Gen11 shared/selector identity must be serviced before clearing `GT_INTR_DW`, and `gen11_gt_reset_one_iir()` must unlock a stuck bit by servicing identity first. Media GT routing can misdeliver GSC/video events if engine topology checks are wrong. Masks must match enabled engines to avoid lost interrupts or storms.

### Test Signals
Signals include engine breadcrumb completion on each class/instance, GuC and media GuC events, GSC/HECI2 interrupts, RPS interrupts, parity errors, IRQ reset/postinstall across generations, interrupt storm recovery via `gen11_gt_reset_one_iir()`, and multi-GT media routing.
