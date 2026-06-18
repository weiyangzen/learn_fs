<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/idlocker_test.go -->
## sources/control-plane/ceph-csi/internal/util/idlocker_test.go

**Purpose:** Tests basic in-process ID locking and selected operation-lock conflict/counter behavior.

**Important APIs and functions:** `TestIDLocker` checks acquire, duplicate-acquire failure, release, and reacquire. `TestOperationLocks` checks clone acquisition blocks expand, clone counters can stack and release, restore counters can stack and release, snapshot create acquire/release, and delete acquire/release.

**Control flow, state, and persistence:** Pure in-memory tests with one lock instance per test and `t.Parallel`.

**Dependencies and integration points:** Uses standard testing. It protects operation serialization used around CSI requests.

**Risks and test signals:** The tests are basic and do not cover concurrent access, delete-vs-restore conflict, modify conflicts, unsupported operations, or counter underflow behavior after extra releases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/idlocker_test.go -->
