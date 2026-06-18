## sources/control-plane/juicefs-csi-driver/pkg/util/dev_minor.go

### Purpose
`dev_minor.go` tracks FUSE device minor numbers for mounted JuiceFS paths. It supports later FUSE abort jobs by remembering the kernel connection minor associated with a mount pod before the mount disappears or becomes corrupted.

### Important APIs, Types, And Functions
`procSelfMountInfoPath` points at `/proc/self/mountinfo` and can be overridden in tests. `devMinorCache` is a `sync.Map`. `SaveFuseDevMinor(podName, mntPath)` parses mountinfo and stores the minor. `GetSavedFuseDevMinor(podName)` retrieves it. `DeleteFuseDevMinor(podName)` removes it. `GetFuseDevMinor(mntPath)` scans mountinfo for the mount point with `fuse` or `fuse.*` fs type and returns the minor.

### Control Flow
Saving is best-effort: if parsing fails or no matching FUSE mount exists, nothing is stored. Retrieval type-asserts the cached value to `uint32`. Deletion simply removes the key.

### State, Persistence, And Dependencies
State is in-memory only and process-local. It is not persisted to Kubernetes despite the TODO suggesting mount pod annotations. Dependencies include `k8s.io/utils/mount.ParseMountInfo`, strings, and sync.

### Integration Points
`PodMount.JUmount` calls `SaveFuseDevMinor` before deleting a no-ref mount pod. `builder.NewFuseAbortJob` can use the saved minor to target `/sys/fs/fuse/connections/<minor>`.

### Risks
The cache is lost on process restart, so recovery after restart may lack dev minor data. `GetSavedFuseDevMinor` assumes all stored values have the expected type. Mountinfo parsing is namespace-dependent; the CSI process must see the relevant mount namespace.

### Test Signals
No tests in this subset. Useful coverage would override `procSelfMountInfoPath` with fixture mountinfo, verify fuse/fuse.* matching, no-match behavior, and cache delete semantics.
