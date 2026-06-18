# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/underfs/WorkerUfsManager.java

Purpose: `WorkerUfsManager` is the worker-side `UfsManager` implementation that lazily discovers and caches mount-specific UFS clients from the master.

Important APIs are constructor, `get(long mountId)`, and `connectUfs`. Control flow first delegates `get` to `AbstractUfsManager`; on local miss it asks `FileSystemMasterClient.getUfsInfo`, validates URI/properties, adds the mount with global plus mount-specific configuration, then returns the cached client. `connectUfs` calls `UnderFileSystem.connectFromWorker` with the worker RPC connect host.

State and persistence include the inherited UFS client/mount cache and a closable `FileSystemMasterClient` registered with the manager closer. Dependencies are Alluxio client/master contexts, UFS abstractions, network address utilities, and status exceptions. Integration points are worker services needing UFS access, especially block/file workers. Risks include master unavailability causing `UnavailableException`, stale cached mount properties until manager recreation, and `Preconditions.checkState` for unknown mount IDs surfacing as unchecked failure. No direct tests are in this subset.
