# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_irq.h

### Purpose
`intel_gt_irq.h` declares GT interrupt handlers and setup helpers and provides small engine IRQ callback helpers.

### Important APIs, Types, And Functions
It declares Gen5/6/8/11 handler, reset, and postinstall functions; `gen11_gt_reset_one_iir()`; `GEN8_GT_IRQS`; `intel_engine_cs_irq()`; and `intel_engine_set_irq_handler()`.

### Control Flow
Top-level IRQ code chooses the generation-specific handler. Engine setup installs an IRQ handler with `smp_store_mb()` so live interrupts see a coherent callback pointer.

### State, Persistence, And Dependencies
The header stores no state but manipulates `engine->irq_handler` through the inline setter. It depends on engine types and integer types.

### Integration Points
Used by i915 IRQ setup, engine initialization, PM IRQ code, and generation-specific interrupt paths.

### Risks
The callback update barrier is required because interrupts can become live during engine allocation/setup. Callers must not pass NULL engines to `intel_engine_cs_irq()` when `iir` is nonzero.

### Test Signals
Compile coverage, live interrupt delivery after handler updates, and generation-specific postinstall/reset tests are relevant.
