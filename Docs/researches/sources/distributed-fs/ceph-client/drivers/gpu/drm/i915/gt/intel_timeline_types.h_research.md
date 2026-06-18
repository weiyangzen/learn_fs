# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_timeline_types.h

## Purpose
`intel_timeline_types.h` defines `struct intel_timeline`, the state container for i915 request sequencing, hardware seqno storage, synchronization history, and lifetime tracking.

## Important APIs, Types, And Functions
The structure contains fence context and seqno, a request-flow mutex, atomic pin and active counts, HWSP map/VMA/offset fields, an initial-breadcrumb flag, outstanding request list, last-request active fence, `i915_active`, retire chain pointer, syncmap pointer, GT/list links, kref, and RCU head.

## Control Flow
The fields are initialized during timeline creation, mutated during pin/enter/request emission/exit/unpin, observed by retirement and debug paths, and finally freed via RCU after kref release.

## State, Persistence, And Dependencies
State is kernel memory plus a GEM-backed HWSP VMA. It persists while referenced and may remain pinned independently of active request tracking. Dependencies include lists, krefs, mutexes, RCU, `i915_active_types`, and forward-declared i915/GT types.

## Integration Points
`intel_timeline.c`, request scheduling, breadcrumbs, semaphores, context code, and debug timeline dumping all rely on this structure.

## Risks
`pin_count` and `active_count` are deliberately separate and must not be collapsed. `last_request` is RCU guarded and does not hold a request reference. Syncmap pruning on idle is safe only when all tracked fences have completed.

## Test Signals
Timeline selftests, KASAN/KCSAN checks, lockdep around mutex/list usage, and stress of request retirement plus debug dumps validate invariants.
