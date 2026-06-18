<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/radoswrapper.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/radoswrapper.go

Purpose: production wrapper implementation adapting go-ceph `rados.IOContext`, `WriteOp`, `ReadOp`, and omap iterators to the internal interfaces.

APIs and control flow: `NewIOContext` wraps an existing `*rados.IOContext`. `CreateWriteOp` and `CreateReadOp` allocate go-ceph ops while retaining the IO context needed by `Operate`. Methods mostly delegate directly to embedded go-ceph operations, with `Operate` passing `rados.OperationNoFlag`.

State and persistence: no independent persistence; all state lives in Ceph/RADOS and go-ceph operation handles. `Release` forwards resource cleanup to go-ceph.

Dependencies: `github.com/ceph/go-ceph/rados`.

Integration points: top-level reftracker callers pass this wrapper around real pools. It is the production counterpart to `FakeIOContext`.

Risks: thin wrappers mean correctness depends on preserving go-ceph operation lifecycle, especially `Release` and assert-version behavior. No direct retries are here; stale writes are surfaced to callers through reftracker error wrapping.

Test signals: no direct unit tests here. Coverage is mostly compile-time and via fake implementation parity; production behavior relies on go-ceph integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/radoswrapper.go -->
