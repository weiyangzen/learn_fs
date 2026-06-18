# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.c

### Purpose
`intel_gt_mcr.c` implements support for multicast/replicated GT registers. It initializes platform steering tables, chooses non-terminated read targets, serializes steering register access, supports unicast and multicast reads/writes/RMWs, reports steering state, and provides an MCR-aware wait helper.

### Important APIs, Types, And Functions
Public APIs are `intel_gt_mcr_init()`, `intel_gt_mcr_lock()`, `intel_gt_mcr_unlock()`, `intel_gt_mcr_lock_sanitize()`, `intel_gt_mcr_read()`, `intel_gt_mcr_read_any()`, `intel_gt_mcr_read_any_fw()`, `intel_gt_mcr_unicast_write()`, `intel_gt_mcr_multicast_write()`, `intel_gt_mcr_multicast_write_fw()`, `intel_gt_mcr_multicast_rmw()`, `intel_gt_mcr_get_nonterminated_steering()`, `intel_gt_mcr_report_steering()`, `intel_gt_mcr_get_ss_steering()`, and `intel_gt_mcr_wait_for_reg()`.

### Control Flow
Initialization sets `gt->mcr_lock`, derives mslice and L3 bank masks from fuse/SSEU registers, and assigns steering tables for media OADDRM, Xe_LPG, DG2, ICL, and related platforms. Reads that need steering choose a valid group/instance based on register range and fuse state; explicit reads/writes program the MCR selector under lock and forcewake. On MTL+, a hardware steering semaphore is acquired in addition to the software spinlock and restored on unlock. Multicast writes force multicast mode before writing all instances.

### State, Persistence, And Dependencies
Persistent state includes `gt->steering_table[]`, `gt->info.l3bank_mask`, `gt->info.mslice_mask`, `gt->default_steering`, and `gt->mcr_lock`. Dependencies include uncore forcewake/MMIO, platform fuses, SSEU topology, GT register definitions, wait helpers, DRM printers, and generation/stepping macros.

### Integration Points
Workaround programming, fault handling, register dumps, OA/perf, debugfs steering reports, and any code touching MCR registers must use this API rather than raw uncore accesses. GT resume sanitizes the hardware semaphore through this module.

### Risks
Steering to a fused or powered-down instance returns zero or drops writes. Lock order matters: `mcr_lock` must precede `uncore->lock`. MTL hardware semaphore timeouts taint CI because firmware/hardware may be holding the lock. Register range tables must remain accurate as platforms add MCR classes.

### Test Signals
Use platforms with L3BANK, MSLICE, LNCF, DSS, INSTANCE0, OADDRM, and media GT steering; verify read-any values are nonzero when expected; stress concurrent MCR access; test MTL semaphore sanitize/resume; validate debugfs steering tables; and exercise timeout paths.
