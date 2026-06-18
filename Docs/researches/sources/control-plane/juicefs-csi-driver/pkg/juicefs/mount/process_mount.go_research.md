## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/process_mount.go

### Purpose
`process_mount.go` implements the direct process-based mount backend. Instead of creating mount pods, it invokes JuiceFS mount commands on the host, creates/deletes subpath directories, checks local mount readiness, unmounts targets and shared refs, and cleans cache directories directly.

### Important APIs, Types, And Functions
`ProcessMount` embeds `SafeFormatAndMount`. `NewProcessMount()` constructs it. Public methods include `JCreateVolume`, `JDeleteVolume`, `JMount`, `GetMountRef`, `UmountTarget`, `JUmount`, `AddRefOfMount`, `CleanCache`, and `RmrDir`. Internal `jmount()` handles CE versus EE mount flow. `defaultCheckTimeout` is shared with pod mode.

### Control Flow
`JCreateVolume` strips readonly options, mounts JuiceFS, creates the subpath with `0777` permissions if absent, fixes permissions after umask, then unmounts. `JDeleteVolume` mounts, checks the subpath, runs `juicefs rmr`, then unmounts. `JMount` pre-creates subpath for readonly mounts, then calls `jmount`. `jmount` uses kernel mount for EE sources without `://`; CE sources create the mount directory, unmount any existing mount, spawn `mount.juicefs` with `JFS_FOREGROUND=1`, and poll `os.Stat` until inode `1` indicates readiness. `JUmount` checks existence/mountpoint/corruption, gets device refs, unmounts the target, and unmounts the shared ref only when it was the last reference.

### State, Persistence, And Dependencies
State is local filesystem and kernel mount state. Cache cleanup deletes `cacheDir/id/raw/chunks`. The backend depends on host JuiceFS binaries (`CeMountPath`, `CeCliPath`, `CliPath`), Kubernetes mount utilities, `os/exec`, syscall env/stat, and util helpers for timeouts, refs, and mountpoint inspection.

### Integration Points
This backend satisfies `MntInterface` for deployments that do not use mount pods. CSI node operations can use it to mount directly into target paths. It shares config settings and logging helpers with pod mode but not Kubernetes object state.

### Risks
`AddRefOfMount` panics, so callers must avoid it in process mode. `jmount` runs the mount command in a goroutine and does not retain or inspect process errors after startup; readiness polling is the only success signal. Cleanup depends on inode `1`, mount table parsing, and timeout behavior, which can vary by filesystem/kernel. Recursive delete uses external JuiceFS CLI and must not receive untrusted paths.

### Test Signals
`process_mount_test.go` covers constructor output, EE mount success/error, CE mount success and error branches, unmount behavior, and corrupted/path existence cases. Additional tests should cover create/delete volume, cache cleanup, and `RmrDir` command selection.
