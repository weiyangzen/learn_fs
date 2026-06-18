<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/fakerados.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/fakerados.go

Purpose: in-memory fake implementation of the reftracker RADOS wrapper interfaces for deterministic unit tests without a Ceph cluster.

APIs and types: `FakeRados` owns an object map; `FakeObj` stores object id, version, xattrs, omap, and data; `FakeIOContext` tracks last object version. `FakeWriteOp` and `FakeReadOp` collect operation steps keyed by internal executor indices. `fakeRadosError` implements `ErrorCode()` for errno-like failures.

Control flow: write and read operations execute in fixed order. Writes apply assert-version, remove, create, xattr, data, omap removal, and omap set steps, then increment the object version and `LastObjVersion` when the object still exists. Reads apply assert-version, object read, and omap lookup, then update `LastObjVersion`. `GetXattr` returns not-found or ENODATA-style errors.

State and persistence: purely in-memory process state. Input byte slices and maps are copied when queued so later caller mutation does not affect fake operations.

Dependencies and integration: mirrors the subset of go-ceph RADOS APIs used by reftracker. Tests build `FakeObj` fixtures directly to validate low-level v1 behavior and top-level idempotency.

Risks: fake operation ordering may not perfectly match librados semantics in all mixed-step combinations. The fake is not concurrency-safe, so it models serial operations rather than true parallel writers. Its version behavior increments after most mutating operations, including creation and metadata changes, which is suitable for current tests but remains a contract to watch.

Test signals: heavily exercised by reftracker, v1, and version tests as the backing store for success, not found, object exists, stale generation, xattr, omap, and read-size scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/fakerados.go -->
