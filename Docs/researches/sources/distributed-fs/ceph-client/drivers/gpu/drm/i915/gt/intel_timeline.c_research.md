# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline.c

## Purpose
`intel_timeline.c` implements i915 request timelines: fence contexts, seqno allocation, hardware status page storage, active tracking, sync-map pruning, pinning, RCU lifetime, and debug dumping.

## Important APIs, Types, And Functions
Public functions include `__intel_timeline_create()`, `intel_timeline_create_from_engine()`, `intel_timeline_pin_map()`, `intel_timeline_pin()`, `intel_timeline_reset_seqno()`, `intel_timeline_enter()`, `intel_timeline_exit()`, `intel_timeline_get_seqno()`, `intel_timeline_read_hwsp()`, `intel_timeline_unpin()`, `__intel_timeline_free()`, GT timeline init/fini, and `intel_gt_show_timelines()`. Internal helpers allocate HWSP VMAs and manage `i915_active` callbacks.

## Control Flow
Creation either borrows an engine status-page VMA at a fixed offset or allocates a private page and marks that it has an initial breadcrumb. Pinning maps the HWSP, pins it high in GGTT, converts the offset to a GGTT address, and acquires active tracking. Entering a timeline adds it to the GT active list and resets HWSP seqno to guard against volatile status-page contents. Seqno allocation increments by one or two depending on initial breadcrumb use; on wrap it advances to another HWSP slot while preserving hardware semaphore constraints. Exit removes idle timelines and drops syncmap history.

## State, Persistence, And Dependencies
State persists in `struct intel_timeline`: kref, mutex, pin/active counts, HWSP map/VMA/offset, seqno, request list, last request fence, syncmap, active object, GT active-list links, and RCU head. Dependencies include GEM object allocation, GGTT pinning, i915 active fences, syncmaps, DMA fence contexts, runtime locking, and DRM printers.

## Integration Points
Contexts and engines use timelines for request ordering and breadcrumbs. Legacy ring submission creates an engine timeline from the status page. Semaphore waits use `intel_timeline_read_hwsp()`. GT debug/error paths call `intel_gt_show_timelines()`.

## Risks
Pin and active counts intentionally model different lifetimes and must stay balanced. HWSP memory may be lost over suspend/resume, so reset-on-enter is critical. RCU access to `from->timeline` and request completion races make `intel_timeline_read_hwsp()` subtle. Seqno wrap and bit-5 MI_FLUSH_DW workarounds can break semaphores if mishandled.

## Test Signals
Selftests include mock and real timeline tests. Useful runtime signals include semaphore waits, seqno wrap tests, suspend/resume, request retirement races, debug timeline dumps under load, and lockdep coverage of timeline mutex/list handling.
