<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/util.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/util.go

### Purpose
`util.go` is a broad utility module for JuiceFS CSI. It handles endpoint parsing, mountinfo parsing, string/slice helpers, time parsing, shell quoting, mount/unmount helpers, mount-command introspection, image/version capability checks, disk usage, Prometheus registry creation, quantity parsing, directory creation, config parsing, internal filename decisions, generic helpers, illegal-character cleanup, and snapshot handle formatting.

### Important APIs, Types, And Functions
Key types are `mountInfo`, `ClientVersion`, and `JuiceConf`. Important functions include `ParseEndpoint`, `GetMountDeviceRefs`, `ContainsString`, `ContainsPrefix`, `ContainSubString`, `GetReferenceKey`, `GetTimeAfterDelay`, `GetTime`, `QuoteForShell`, `StripReadonlyOption`, `StripPasswd`, `RandStringRunes`, `DoWithTimeout`, `CheckDynamicPV`, `UmountPath`, `GetMountPathOfSidecar`, `GetMountPathOfPod`, `parseMntPath`, `CheckExpectValue`, `ImageResol`, `GetDiskUsage`, `NewPrometheus`, `ParseToBytes`, `Exists`, `MkdirIfNotExist`, version support functions, `ParseConfig`, `ContainsEnv`/volume helpers, `GetMountOptionsOfPod`, `GetJfsInternalFileName`, generic copy/merge/sort helpers, `ParseSubdirFromMountOptions`, `IsConfigEncrypted`, `CopySlice`, `RemoveIllegalChars`, `EnsureSnapshotHandle`, and `ParseSnapshotHandle`.

### Control Flow
Endpoint parsing accepts `tcp` or `unix`, removes stale unix sockets, and returns scheme/address. Mountinfo parsing reads `/proc/self/mountinfo`, parses fields around the `-` separator, finds the backing mount for a path, and returns other mountpoints sharing the same major/minor and filesystem type. Time helpers now emit RFC3339 UTC delayed timestamps and parse either RFC3339 or legacy local-time layout. Mount command parsing reads the third command element, takes the final newline-separated command, strips leading `exec`, and extracts `/jfs/<id>` or `/mnt/jfs` mount paths. Version helpers parse image tags and `juicefs version` strings, then compare CE/EE minimums for fuse pass, binary upgrade, quota path creation, and config encryption. `DoWithTimeout` runs a function in a child context and races parent cancellation, child deadline, and function completion.

### State, Persistence, And Dependencies
The file reads `/proc/self/mountinfo`, invokes `umount`, uses `syscall.Statfs`, creates directories, removes unix socket files, parses JSON, and creates Prometheus registries. Dependencies include Kubernetes `corev1`, Prometheus, klog, `k8s.io/utils/io.ConsistentRead`, standard filesystem/process packages, and project common constants.

### Integration Points
These helpers are shared across CSI endpoint startup, node mount cleanup, mount-pod and sidecar introspection, webhook decisions, controller cleanup, metrics exposure, snapshot identity, and version-gated feature rollout.

### Risks
`parseMntPath` and `GetMountOptionsOfPod` depend on specific shell command layout and can panic if `strings.Fields` returns an empty slice. `DoWithTimeout` can return `"function timeout"` when the child deadline fires even if the goroutine is about to return, and it does not wait for non-cooperative functions to stop. `Exists` returns true for permission and other stat errors. `StripPasswd` is heuristic and may mishandle uncommon URI shapes. Version parsing treats many unrecognized tags as dev and therefore unsupported. `GetMountDeviceRefs` is Linux/procfs-specific. `RemoveIllegalChars` removes all non-ASCII printable characters, which can discard valid Unicode names.

### Test Signals
High-value signals include endpoint parse/remove errors, mountinfo malformed lines, symlink/corrupt mountpoint paths, time-zone round trips, unmount tolerated messages, mount command variants, image/version threshold boundaries, byte parsing with unit suffixes, config encryption JSON variants, internal filename prefix behavior, snapshot handle parse errors, and illegal-character filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/util.go -->
