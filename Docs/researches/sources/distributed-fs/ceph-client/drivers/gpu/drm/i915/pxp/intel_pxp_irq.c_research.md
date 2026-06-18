# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_irq.c

Purpose: Handles KCR/PXP interrupt events and enables/disables PXP interrupt delivery.

Important APIs/functions: `intel_pxp_irq_handler()`, `intel_pxp_irq_enable()`, and `intel_pxp_irq_disable()`.

Control flow: IRQ handler requires `gt->irq_lock`, ignores empty IIR, marks termination in progress for terminated/app-terminated events, sets invalidation and event-source bits, records reset-complete events, and queues `session_work`. Enable resets stale GEN11_KCR IIR once, unmasks/enables GEN12 PXP interrupt bits, and sets `irq_enabled`. Disable requires PXP inactive, masks interrupts, synchronizes IRQs, resets IIR, and flushes session work.

State/persistence: Mutates `pxp->session_events`, `irq_enabled`, `arb_is_valid` via termination marking, and the `termination` completion state.

Dependencies/integration: Uses GT IRQ lock, GEN11/GEN12 interrupt registers, uncore MMIO, `intel_synchronize_irq()`, PXP session worker, and runtime PM-aware hardware init/fini.

Risks: Events are bit-accumulated under irq_lock and consumed asynchronously; missing locks can lose events. Disabling while active is warned because restart must force global termination after re-enable. Worker flushing during disable prevents stale session work after hardware teardown.

Test signals: Debugfs termination path simulates interrupt handling. Runtime logs show session event processing and termination completion.
