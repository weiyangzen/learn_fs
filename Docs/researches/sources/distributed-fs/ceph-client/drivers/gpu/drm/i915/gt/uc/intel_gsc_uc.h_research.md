# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.h

### Purpose
`intel_gsc_uc.h` defines the top-level GSC uC state structure and public lifecycle/status helpers.

### Important APIs, Types, And Functions
`struct intel_gsc_uc` embeds `struct intel_uc_fw`, release/security version fields, local VMA/iomap, pinned context, workqueue/work/action bits, and a proxy substructure. It declares init, fini, suspend/resume, flush, load-start, and load-status functions plus inline `is_supported`, `is_wanted`, and `is_used` helpers.

### Control Flow
The header contains inline status checks only; full lifecycle flow is implemented in `intel_gsc_uc.c`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State persists for the GT lifetime and is protected by `gt->irq_lock` for action bits and a mutex for proxy binding. Dependencies include firmware core types, VMA/context declarations, and MEI component declarations. Integration spans firmware upload, proxy, HECI submission, HuC auth, and debugfs. Risks include incorrect status interpretation and unbalanced object lifetimes. Test signals are compile coverage and consistent status transitions through supported/wanted/used helpers.
