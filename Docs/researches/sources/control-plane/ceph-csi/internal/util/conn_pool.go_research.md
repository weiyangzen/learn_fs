<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/conn_pool.go -->
## sources/control-plane/ceph-csi/internal/util/conn_pool.go

**Purpose:** Implements a reference-counted pool of go-ceph `rados.Conn` objects keyed by monitor list, user, and key contents, with periodic garbage collection of idle connections.

**Important APIs and types:** `ConnPool` stores interval, expiry, timer, lock, and `map[string]*connEntry`. `NewConnPool`, `Destroy`, `Get`, `Copy`, `Put`, `gc`, `generateUniqueKey`, `getConn`, and `connEntry` methods manage lifecycle and reference counts.

**Control flow, state, and persistence:** `Get` reads the key file to build a stable key, checks existing entries under an RW lock, creates and connects a new `rados.Conn` if absent, then inserts it under a write lock with race handling. `Copy` increments reference count for an existing pointer. `Put` decrements but does not destroy immediately. `gc` destroys entries with zero users and age greater than expiry, then resets the timer. `Destroy` stops GC, panics if entries still have users, and shuts down all connections.

**Dependencies and integration points:** Depends on `sync`, `time`, `os`, and go-ceph `rados`. `ClusterConnection` and pool/object helpers use the global pool for Ceph access.

**Risks and test signals:** Reference leaks prevent GC and make `Destroy` panic. Double `Put` can decrement below zero because no guard prevents it. Creating a connection outside the write lock avoids blocking but can race, so the loser destroys the extra connection. The unique key includes keyfile contents, not path, which is correct for rotated temp key files but reads secret material into memory. Tests use a fake getter and validate reuse, refcounting, and GC without needing a real Ceph cluster.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/conn_pool.go -->
