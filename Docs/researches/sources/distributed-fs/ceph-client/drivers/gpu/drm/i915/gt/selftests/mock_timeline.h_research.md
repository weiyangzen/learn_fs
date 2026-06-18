# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.h

### Purpose
`mock_timeline.h` declares the mock timeline lifecycle helpers for i915 selftest code.

### Important APIs, Types, And Functions
It forward-declares `struct intel_timeline` and declares `mock_timeline_init(struct intel_timeline *timeline, u64 context)` plus `mock_timeline_fini(struct intel_timeline *timeline)`.

### Control Flow
The header has no runtime control flow; it gates inclusion with `__MOCK_TIMELINE__`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends only on Linux integer types. It integrates with selftest modules that want mock timelines without pulling implementation details into every test. Risks are prototype drift with `mock_timeline.c` or accidental use outside selftest-only contexts. Test signals are compile-time coverage by mock timeline users.
