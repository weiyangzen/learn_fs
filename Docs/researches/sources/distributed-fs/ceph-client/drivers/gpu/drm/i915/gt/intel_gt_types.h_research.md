# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_types.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_types.h

### Purpose
`intel_gt_types.h` defines the central `struct intel_gt` object and related GT-wide enums/types. It is the persistent state model for a graphics, tile, or media GT in the i915 driver.

### Important APIs, Types, And Functions
Major definitions include `struct intel_mmio_range`, `enum intel_steering_type`, `enum intel_submission_method`, `struct gt_defaults`, `enum intel_gt_type`, `struct intel_gt`, `struct intel_gt_definition`, `enum intel_gt_scratch_field`, and `intel_gt_support_legacy_fencing()`.

### Control Flow
The type layout supports initialization flow from early allocation through MMIO setup, engine/UC/PM init, runtime operation, sysfs/debugfs registration, suspend/resume, reset, and final release. Engine arrays provide lookup by global id and by class/instance; nested structs group TLB, timeline, request, watchdog, PM stats, CCS, info, MOCS, and sysfs state.

### State, Persistence, And Dependencies
`struct intel_gt` persists device ownership pointers, uncore and GGTT pointers, UC/GSC/WOPCM, TLB invalidation batching, workaround lists, active timelines, request retirement, watchdog work, wakerefs, closed VMAs, reset state, awake stats, clock frequency, LLC/RC6/RPS, interrupt masks, engines, submission method, CCS slices, kernel VM, buffer pool, scratch VMA, migration context, MCR steering, physical MMIO base, topology/info/hwconfig, MOCS indexes, sysfs kobjects, wedge work, perf data, and GGTT list linkage.

### Integration Points
Included by most GT modules and embedded indirectly in the top-level i915 device's GT array. It connects engine, UC, PM, reset, memory, interrupt, sysfs, debugfs, perf, and MCR subsystems through shared state.

### Risks
Because it is the central shared state object, lifecycle and locking rules around each field are critical. `irq_lock` is a pointer to support per-GT allocation, MCR lock order is documented, stats use seqcount under wakeref mutex, and union-like subsystem ownership requires init/fini symmetry. Adding fields without clear ownership can create teardown races.

### Test Signals
Multi-GT probe, suspend/resume, runtime PM, engine init/fini, MCR steering, sysfs/debugfs registration, request retirement, and wedge/reset selftests all validate that the shared state model remains coherent.
