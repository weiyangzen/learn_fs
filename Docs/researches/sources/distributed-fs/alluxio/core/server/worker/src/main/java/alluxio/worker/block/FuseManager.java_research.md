## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/FuseManager.java

### Purpose
`FuseManager` owns the lifecycle of the worker-internal Alluxio FUSE application when worker FUSE is enabled.

### Important APIs and Types
- Constructor stores `FileSystemContext` and creates a `Closer`.
- `start()` creates a `FileSystem` and launches FUSE with `FuseOptions`.
- `close()` unmounts and closes registered resources.

### Control Flow
`start` registers a `FileSystem` in the resource closer and invokes `AlluxioFuse.launchFuse(..., false)`. Errors are caught broadly and logged so worker startup does not immediately propagate the FUSE launch failure. `close` attempts forced unmount if FUSE was launched, logs unmount errors, then closes the resource closer.

### State and Persistence
Runtime state is the FUSE unmount handle and closeable resources. It does not persist Alluxio block data directly.

### Dependencies and Integration Points
Created by `DefaultBlockWorker` and started only when `WORKER_FUSE_ENABLED` is true. Depends on Alluxio FUSE, file-system client, and worker file-system context.

### Risks
- Launch failures are logged but swallowed, so callers need logs/health checks to detect missing FUSE.
- TODO notes launch can block and may deserve its own thread/status tracking.
- Already-mounted handling is not implemented.

### Test Signals
No direct test surfaced in the searched references; coverage is mostly through worker lifecycle tests when FUSE is disabled.
