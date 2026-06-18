# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.c

### Purpose
`mock_timeline.c` provides a tiny initializer/finalizer for `struct intel_timeline` instances used by selftests that do not need a full GT-backed timeline.

### Important APIs, Types, And Functions
It exports `mock_timeline_init()` and `mock_timeline_fini()`. The code initializes `timeline->fence_context`, `timeline->mutex`, `timeline->last_request`, `timeline->requests`, `timeline->sync`, and `timeline->link`, while deliberately leaving `timeline->gt` as `NULL`.

### Control Flow
Initialization is direct field setup followed by `i915_syncmap_init()`. Finalization releases only the sync map via `i915_syncmap_free()`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The object is caller-owned and persists only for the selftest lifetime. It depends on `intel_timeline.h`, active fence/list primitives, mutexes, and sync maps. It integrates with mock request/timeline tests that require a valid fence context without hardware. Risks are limited to callers expecting GT-backed behavior or forgetting to call the finalizer. Test signals are leak-free sync-map teardown and correct fence-context propagation.
