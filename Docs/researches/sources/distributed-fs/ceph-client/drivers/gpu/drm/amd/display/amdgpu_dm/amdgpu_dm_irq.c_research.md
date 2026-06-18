# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq.c

## Purpose
`amdgpu_dm_irq.c` implements Display Manager's IRQ indirection layer above the base AMDGPU IRQ framework. It lets DC subcomponents register high-context interrupt callbacks and low-context workqueue callbacks, maps hardware IV entries to DC IRQ sources, controls DC interrupt enablement, and manages HPD/HPDRX, vblank, pageflip, vline, vupdate, and DMUB outbox IRQ sources.

## Important APIs, types, and functions
Public APIs are `amdgpu_dm_irq_init()`, `amdgpu_dm_irq_fini()`, `amdgpu_dm_irq_register_interrupt()`, `amdgpu_dm_irq_unregister_interrupt()`, suspend/resume hooks, `amdgpu_dm_set_irq_funcs()`, `amdgpu_dm_outbox_init()`, `amdgpu_dm_hpd_init()`, and `amdgpu_dm_hpd_fini()`. Internal dispatch uses `amdgpu_dm_irq_handler()`, `amdgpu_dm_irq_immediate_work()`, `amdgpu_dm_irq_schedule_work()`, `dm_irq_work_func()`, and handler removal/cleanup helpers.

## Control flow
Initialization creates high and low handler lists for every DC IRQ source. Registration validates params, allocates handler data, initializes work for low-context handlers, and appends it under a spinlock. The base AMDGPU `process` hook maps the interrupt vector to a DC source, acknowledges it, runs high-context handlers immediately, and queues low-context handlers on `system_highpri_wq`. Suspend disables HPD/HPDRX sources and flushes HPD work; resume re-enables HPDRX early and HPD late.

## State and persistence behavior
State is runtime-only in `adev->dm`: handler-list tables, a spinlock, queued work items, and handler records with callback, argument, DM pointer, and source. Hardware interrupt state is controlled through `dc_interrupt_set()` and AMDGPU IRQ reference counts for HPD sources.

## Dependencies and integration points
It depends on AMDGPU IRQ infrastructure, DRM polling/connector iteration, AMD DC interrupt mapping/ack/set APIs, HPD numbering, system workqueues, and CRTC `otg_inst`. It integrates DC registration sites with base driver IRQ source functions.

## Risks and edge cases
High-context handlers execute under a spinlock and must not sleep. Low-context duplicate handler allocation during interrupt storms must be cleaned up later. Unregistration by handler pointer may find only the first matching object. HPD source count mismatches require fallback direct DC control. CRTC IRQ state changes also disable idle optimizations, affecting power behavior.

## Test signals
Exercise registration/unregistration, high and low dispatch, interrupt storms while work is pending, teardown with queued work, invalid parameter rejection, HPD/HPDRX init/fini/suspend/resume, vblank/pageflip/vline/vupdate/DMUB mappings, analog polling setup, and lockdep IRQ-context checks.
