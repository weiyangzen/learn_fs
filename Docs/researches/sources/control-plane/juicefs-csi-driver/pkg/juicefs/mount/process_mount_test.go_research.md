## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/process_mount_test.go

### Purpose
`process_mount_test.go` validates direct process mount behavior without performing real JuiceFS mounts. It uses GoMock mount interfaces and monkey patches filesystem/process functions to exercise success and failure branches.

### Important APIs, Types, And Functions
Tests cover `NewProcessMount`, `ProcessMount.JUmount`, and `ProcessMount.JMount`. Mocked dependencies include `k8sMount.PathExists`, `k8sMount.IsNotMountPoint`, `util.GetMountDeviceRefs`, `os.MkdirAll`, `os.Stat`, `syscall.Environ`, and `exec.Cmd.Run`.

### Control Flow
`TestProcessMount_JUmount` verifies successful unmount, PathExists errors, and unmount errors. `TestProcessMount_JMount` splits EE behavior (delegates to `Mount`) from CE behavior (directory checks, existing mount unmount, command run, inode readiness), then covers stat errors, inode-not-ready timeout path, PathExists errors, mkdir errors, mountpoint check errors, and pre-unmount errors.

### State, Persistence, And Dependencies
The tests do not persist real mount state. They depend heavily on monkey-patched global functions and GoMock expectations. Fake file info types from driver mocks provide inode `1` or `2` to simulate ready/unready mountpoints.

### Integration Points
These tests guard the local backend used by CSI mount operations when not using pod mode. They also protect interactions with `k8s.io/utils/mount.SafeFormatAndMount`.

### Risks
There is no direct coverage of `JCreateVolume`, `JDeleteVolume`, `GetMountRef`, `CleanCache`, or `RmrDir`. The CE mount command runs in a goroutine in production; monkey-patched `Run` returning nil does not verify process lifecycle or stderr handling. Timeout branches can be slow or flaky if contexts change.

### Test Signals
Failures usually indicate changed mountpoint readiness logic, changed EE/CE source classification, or changed unmount reference behavior.
