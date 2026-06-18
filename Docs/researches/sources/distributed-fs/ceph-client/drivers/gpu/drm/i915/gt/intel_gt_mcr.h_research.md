# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_mcr.h

### Purpose
`intel_gt_mcr.h` exposes the MCR steering API and iteration helper for code that reads or writes multicast/replicated GT registers.

### Important APIs, Types, And Functions
It declares MCR init, lock/unlock/sanitize, explicit and read-any accessors, unicast/multicast writes, multicast RMW, steering lookup/report helpers, MCR wait helper, `_HAS_SS()`, and `for_each_ss_steering()`.

### Control Flow
Consumers use the API to avoid terminated reads/writes. The subslice steering iterator maps logical DSS/subslice IDs to group/instance pairs and skips fused-off units through SSEU topology checks.

### State, Persistence, And Dependencies
The header owns no state but depends on `struct intel_gt`, MCR register types, SSEU helpers, and graphics IP version macros.

### Integration Points
Included by workaround, register access, debugfs, and GT fault code that needs safe MCR access.

### Risks
Callers of `_fw` variants must already hold forcewake and `mcr_lock`. Incorrect use of raw MMIO for MCR registers bypasses the protections defined here.

### Test Signals
Compile and runtime coverage of `for_each_ss_steering()`, explicit MCR access, and `_fw` variants under lockdep are important.
