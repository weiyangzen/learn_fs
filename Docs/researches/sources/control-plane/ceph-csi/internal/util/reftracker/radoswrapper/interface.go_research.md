<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/interface.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/interface.go

Purpose: declares narrow wrapper interfaces around go-ceph RADOS types so reftracker logic can run against both real RADOS and the fake test implementation.

APIs: `IOContextW` exposes last-version lookup, xattr read, and factory methods for read/write ops. `WriteOpW` supports create, remove, xattr, full-object write, omap set/remove, assert-version, operate, and release. `ReadOpW` supports data reads, omap lookup by keys, assert-version, operate, and release. `ReadOpOmapGetValsByKeysStepW` exposes iterator `Next`.

Control flow and state: interfaces themselves hold no state, but they define the atomic operation surface used by v1 `Init`, `Add`, `Remove`, and `readObjectByKeys`.

Dependencies: imports go-ceph `rados` for create options, read steps, and omap key/value types.

Integration points: implemented by `radoswrapper.go` for production and `fakerados.go` for tests. This boundary is the main testability seam for reftracker persistence and concurrency checks.

Risks: the interface is intentionally minimal; any reftracker change needing additional RADOS features must update both real and fake implementations. Semantics of `AssertVersion` and `GetLastVersion` depend on go-ceph behavior and fake parity.

Test signals: validated indirectly because compile-time assertions in implementations require interface conformance and tests run reftracker logic through fake `IOContextW`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/interface.go -->
