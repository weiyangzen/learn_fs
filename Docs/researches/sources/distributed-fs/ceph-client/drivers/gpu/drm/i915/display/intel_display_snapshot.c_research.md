# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_snapshot.c

## Purpose
This file captures, prints, and frees display diagnostic snapshots. It packages display device info, runtime info, module/display parameters, DMC state, and display IRQ state for later error reporting without requiring live hardware reads for every field.

## Important APIs, Types, and Functions
`struct intel_display_snapshot` stores the `intel_display` pointer, `intel_display_device_info`, `intel_display_runtime_info`, `intel_display_params`, `intel_dmc_snapshot *`, and `intel_display_irq_snapshot *`. `intel_display_snapshot_capture()` allocates and fills the snapshot with `GFP_ATOMIC`. `intel_display_snapshot_print()` emits the stored data through a `drm_printer`. `intel_display_snapshot_free()` releases copied params and child snapshots.

## Control Flow
Capture allocates zeroed memory, stores the display pointer, copies static/runtime display info, copies current display parameters, then captures IRQ and DMC snapshots. Print returns immediately for null snapshots and otherwise prints device info, parameters, IRQ snapshot, and DMC snapshot. Free tolerates null, frees nested param allocations, then frees IRQ, DMC, and the snapshot object.

## State and Persistence Behavior
The snapshot is persistent diagnostic state after capture. The info/runtime/params fields are copies, while DMC and IRQ snapshots are separate allocated objects owned by the snapshot. The original display pointer is kept for driver-name access during printing, so it is not a fully standalone object.

## Dependencies and Integration Points
Dependencies include display device info, display params, display IRQ snapshot, DMC snapshot, overlay include context, slab allocation, and DRM printer/driver metadata. It likely integrates with error capture, debug dumps, and crash/reset diagnostics.

## Risks
`GFP_ATOMIC` allocation can fail, producing a null snapshot that callers and printers must tolerate. Child snapshot capture failures are not fatal but produce partial dumps. The stored display pointer must outlive printing. `intel_display_snapshot_free()` assumes child snapshots can be freed with `kfree()`, matching their capture APIs.

## Test Signals
Signals include forced error-state capture, snapshot printing from debug paths, allocation-failure tolerance, KASAN/lockdep clean free paths, and dumps showing device info, params, IRQ, and DMC sections without live MMIO faults.
