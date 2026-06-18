<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/conn_pool_test.go -->
## sources/control-plane/ceph-csi/internal/util/conn_pool_test.go

**Purpose:** Tests connection pool reference counting, key-based reuse, and garbage collection using a fake getter that avoids connecting to Ceph.

**Important APIs and functions:** `fakeGet` mirrors `ConnPool.Get` up to the real `Connect` call and inserts a new `rados.Conn`. `TestConnPool` covers first get, second get reusing the same map entry and increasing users, `Put` decreasing users, forced expiry, and `gc` removing the idle entry.

**Control flow, state, and persistence:** The test creates a temp keyfile, a pool with long durations, and subtests that share `conn`/`unique` state, so it intentionally does not run subtests in parallel. It mutates `lastUsed` to force expiration.

**Dependencies and integration points:** Uses go-ceph `rados.NewConn` but does not connect to a cluster. It exercises internal pool data structures directly.

**Risks and test signals:** Good unit signal for reuse and GC. It does not cover real `ParseCmdLineArgs`, `ReadConfigFile`, connect failures, `Copy`, `Destroy` panic, or double `Put` underflow. Because it reaches into internals, refactors need coordinated test updates.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/conn_pool_test.go -->
