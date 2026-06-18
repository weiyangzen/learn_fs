# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_irq.c

## Purpose
`xe_irq.c` owns Xe interrupt initialization, installation, suspend/resume, reset, top-level dispatch, engine interrupt enabling, and MSI-X vector management. It routes display, GT engine, GuC, GSC proxy, PXP, I2C, MERT, hardware error, and memory-backed interrupt events.

## Important APIs, Types, And Functions
- Public API: `xe_irq_init()`, `xe_irq_install()`, `xe_irq_suspend()`, `xe_irq_resume()`, `xe_irq_enable_hwe()`, `xe_irq_msix_request_irq()`, and `xe_irq_msix_free_irq()`.
- Legacy and tiled top-level handlers are `xelp_irq_handler()` and `dg1_irq_handler()`.
- VF memory-backed path uses `vf_mem_irq_handler()` and `xe_memirq_handler()`.
- GT dispatch is centralized in `gt_irq_handler()`, which reads `GT_INTR_DW`, resolves identity with `gt_engine_identity()`, chooses primary/media GT with `pick_engine_gt()`, and calls engine or subsystem handlers.
- Reset/postinstall functions mask/unmask register blocks, display, I2C, GU misc, and memory IRQ state.
- MSI-X support uses an xarray to track static and dynamic vectors and installs a GuC2Host vector plus a default HWE vector.

## Control Flow
`xe_irq_init()` initializes locking and probes MSI-X capability. `xe_irq_install()` resets hardware state, allocates MSI or MSI-X vectors, requests IRQs, enables the atomic IRQ gate, postinstalls masks/enables, and registers managed uninstall. Runtime IRQ handlers first check `xe->irq.enabled`, disable/ack master state, dispatch GT and platform-specific subevents, re-enable master interrupts, and perform display re-enable using GU misc ack data. Suspend clears `enabled`, synchronizes all active vectors, and resets interrupts; resume resets, postinstalls, and re-enables HWE interrupts for each GT.

## State And Persistence
Persistent state lives under `xe->irq`: spinlock, enabled atomic, MSI-X vector count, and xarray vector allocations. Hardware interrupt masks and enable registers are reset and reprogrammed across install, suspend, resume, and uninstall. MSI-X dynamic vector allocations persist until explicitly freed or global uninstall.

## Dependencies And Integration Points
This file integrates with PCI MSI/MSI-X APIs, Xe display IRQ code, GT/HWE IRQ handling, GuC, GSC proxy, PXP, hardware error handling, I2C, MERT, SR-IOV detection, memory IRQ support, and tile/GT topology helpers. It also relies on register definitions in `regs/xe_irq_regs.h`.

## Risks
Interrupt ordering is delicate: master disable/ack, lower-level ack, display re-enable, and IIR clearing must avoid lost or relatched interrupts. `identity[32]` is reused per bank, so bank-local bit handling must remain consistent. MSI-X vector xarray teardown uses `xa_for_each()` while freeing entries, which depends on xarray iteration semantics. VF paths require memory IRQ support on newer graphics versions. Top-level DPC containment handling returns early when MMIO reads all ones.

## Test Signals
Coverage should include MSI and MSI-X install/uninstall, dynamic MSI-X request/free, suspend/resume IRQ quiescing, VF memory IRQ delivery, display and GU misc events, I2C/MERT interrupt forwarding, media-vs-primary GT routing, PXP/GSC/HECI routing, and DPC containment reads. Interrupt storm and missed-interrupt tests are important.
