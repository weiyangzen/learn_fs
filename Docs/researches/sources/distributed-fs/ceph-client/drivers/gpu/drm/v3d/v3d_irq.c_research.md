<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_irq.c

Purpose: Handles V3D core and hub interrupts, signals job fences, services binner out-of-memory by allocating overflow memory, logs MMU/GMP faults, and manages IRQ setup/enable/disable/reset.

Important APIs/types/functions: `V3D_CORE_IRQS()` and `V3D_HUB_IRQS()` compute generation-dependent masks. `v3d_overflow_mem_work()` creates a 256 KiB BO and attaches it to the active bin/render job. `v3d_irq_signal_fence()` updates stats, clears active job, and signals IRQ fence. `v3d_irq()` handles OUTOMEM, bin/render/CSD completion, GMP violations, and shared-line fallback. `v3d_hub_irq()` handles TFU completion and MMU fault reporting. `v3d_irq_init()`, `v3d_irq_enable()`, `v3d_irq_disable()`, and `v3d_irq_reset()` manage interrupt lifecycle.

Control flow: Probe clears pending interrupts, requests either separate core/hub IRQs or one shared IRQ, then enables masks. Completion IRQs acknowledge registers first, signal active job fences, and return handled. OUTOMEM schedules work because BO allocation cannot run in interrupt context.

State and persistence: State includes IRQ numbers, single-line flag, active queue jobs, overflow work item, and temporary overflow BOs linked to render-job cleanup lists.

Dependencies and integration points: Integrates platform IRQs, DRM logging, V3D BO/MMU, scheduler stats, tracepoints, and generation-specific register maps.

Risks and test signals: Risks include NULL active jobs on spurious completion IRQs, races between overflow work and job completion, MMU fault recovery only logging, and IRQ mask mistakes. Tests should cover separate/shared IRQ configurations, bin/render/TFU/CSD completions, OOM overflow path, reset disable synchronization, and fault logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_irq.c -->
