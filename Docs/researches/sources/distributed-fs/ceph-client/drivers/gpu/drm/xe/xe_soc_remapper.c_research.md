<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.c

Purpose: initializes optional SoC remapper hooks for telemetry and system-control regions and implements locked MMIO updates for remapper index fields.

Important APIs and control flow: `xe_soc_remapper_init()` checks device info flags, initializes `xe->soc_remapper.lock` when any remapper exists, and assigns function pointers for telemetry and sysctrl region setters. Setter helpers call `xe_soc_remapper_set_region()`, which takes `spinlock_irqsave` and performs `xe_mmio_rmw32()` on root tile MMIO register `SG_REMAP_INDEX1`.

State and dependencies: state lives in `xe->soc_remapper`, including function pointers and lock. Depends on remapper register definitions, root tile MMIO, and device capability flags.

Risks and test signals: function pointers remain NULL when the corresponding feature flag is absent; callers must check before invoking. Tests should validate masked RMW field encoding and concurrent setter serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.c -->
