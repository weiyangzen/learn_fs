## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsManager.java

### Purpose
`UfsManager` is the service-level registry interface for UFS clients keyed by Alluxio mount ids, root, and journal locations.

### Important APIs, Types, And Functions
The nested `UfsClient` lazily creates and caches an `UnderFileSystem` from a supplier and exposes `acquireUfsResource()` plus `getUfsMountPointUri()`. The outer interface declares `addMount`, `addMountWithRecorder`, `removeMount`, `get`, `getRoot`, `getJournal`, and `hasMount`.

### Control Flow
`UfsClient.acquireUfsResource` uses an `AtomicReference` compare-and-set to initialize the underlying UFS once. If two callers race, the losing newly created UFS is closed. A metrics counter named `UfsSessionCount-Ufs:<escaped mount>` is incremented for each acquired resource and decremented when the `CloseableResource` is closed.

### State And Persistence
The nested client stores the cached UFS, mount URI, supplier, and session counter in memory. The manager implementation, outside this file, stores mount mappings. No direct persistence occurs here.

### Dependencies And Integration Points
Integrates with `UnderFileSystem`, `UnderFileSystemConfiguration`, `Recorder`, `CloseableResource`, Alluxio metrics, and status exceptions. Used by master/worker services to share and lifecycle-manage UFS access.

### Risks
Callers must close the returned `CloseableResource` or the session counter leaks. If the supplier returns an unusable UFS or throws unchecked exceptions, acquire fails. The cached UFS is not replaced after later failures unless implementation removal/close logic handles it elsewhere.

### Test Signals
No direct tests in this subset. Metric/session behavior is typically covered by UFS manager implementation tests elsewhere.
