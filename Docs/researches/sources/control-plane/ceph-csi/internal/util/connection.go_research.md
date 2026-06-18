<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/connection.go -->
## sources/control-plane/ceph-csi/internal/util/connection.go

**Purpose:** Wraps pooled RADOS connections with helper methods for CephFS, RBD, OSD, task, NFS, IO context, FSID, and address access.

**Important APIs and types:** `ClusterConnection` stores `*rados.Conn`, credentials, and a discard setting. Package globals create `connPool` with long interval/expiry. Methods include `Connect`, `Destroy`, `Copy`, `GetIoctx`, `GetFSAdmin`, `GetOSDAdmin`, `GetFSID`, `GetRBDAdmin`, `GetTaskAdmin`, `GetNFSAdmin`, and `GetAddrs`.

**Control flow, state, and persistence:** `Connect` lazily obtains a pooled connection and stores credentials. `Destroy` returns the connection to the pool but does not nil the field. `Copy` creates another `ClusterConnection` around the same pooled connection with an incremented refcount. Admin and IO context getters validate that a connection exists and then instantiate go-ceph admin wrappers or open a pool IO context.

**Dependencies and integration points:** Depends on go-ceph RADOS, CephFS admin, RBD admin, OSD admin, and NFS admin packages. It is the central utility boundary used by RBD, CephFS, NFS, and blocklist helpers.

**Risks and test signals:** Callers must balance each `Connect`/`Copy` with `Destroy`. Because `Destroy` does not nil `cc.conn`, calling it twice can double-decrement the pool refcount. Pool-not-found errors are normalized to `ErrPoolNotFound`. No direct tests in this subset cover this wrapper; connection behavior is mainly integration-tested with Ceph.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/connection.go -->
