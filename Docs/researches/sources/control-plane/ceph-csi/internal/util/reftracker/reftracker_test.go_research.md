<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftracker_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/reftracker_test.go

Purpose: top-level behavior tests for the public reftracker API using the fake RADOS backend.

Important coverage: `TestRTAdd` verifies missing names/refs, bulk creation, and overlapping additions that do not double-count existing refs. `TestRTRemove` verifies missing refs validation, missing object idempotence, no-op removal of unknown refs, deletion when all tracked refs are removed, one-by-one removal, repeated lifecycle cycles, and overlap add followed by distinct removals. `TestRTMask` verifies mask operations, deletion when only masked refs remain, mask plus remove combinations, masked refs blocking future `Add`, and masked refs being removable with `Normal` before re-add.

Control flow and state: each subtest creates a fresh `FakeIOContext` and usually runs in parallel, avoiding shared fake state. Tests observe only returned booleans/errors at the public layer, leaving detailed object shape checks to v1 tests.

Dependencies: `testify/require`, fake RADOS, and `reftype`.

Risks highlighted: duplicate subtest names appear for two remove cases, which can make targeted test runs less clear. There is no explicit test of public retry behavior because retrying is a caller concern.

Test signal quality: strong for idempotency and mask semantics; weaker for concurrent writer interleavings because fake usage is serial.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftracker_test.go -->
