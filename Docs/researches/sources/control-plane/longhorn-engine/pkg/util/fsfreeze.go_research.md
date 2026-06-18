## sources/control-plane/longhorn-engine/pkg/util/fsfreeze.go

### Purpose
`fsfreeze.go` provides helper functions for freezing and safely unfreezing filesystems mounted from Longhorn block devices. It is mainly relevant to `tgt-blockdev` volumes during shutdown or recovery paths where a filesystem may have been mounted inside the engine container namespace.

### Important APIs, Types, And Functions
Path helpers are `GetFreezePointFromDevicePath`, `GetFreezePointFromVolumeName`, and `GetDevicePathFromVolumeName`. Runtime helpers are `FreezeFilesystem`, `UnfreezeFilesystem`, `UnfreezeAndUnmountFilesystem`, and `UnfreezeFilesystemForDevice`. Constants define `fsfreeze`, the not-frozen error substring, `/var/lib/longhorn/freeze`, the Longhorn device path prefix, and a five-second unfreeze timeout.

### Control Flow
Freeze runs `fsfreeze -f` with no timeout because the command cannot safely be cancelled. Unfreeze runs `fsfreeze -u` with a short timeout and returns `(false, nil)` when the kernel reports the filesystem was not frozen. `UnfreezeAndUnmountFilesystem` unfreezes then calls Kubernetes mount cleanup. `UnfreezeFilesystemForDevice` first checks the canonical freeze point, then scans all mount points for the device and unfreezes any matching mount without unmounting non-canonical mounts.

### State, Persistence, And Dependencies
The file manipulates mount state and frozen filesystem state, not repository state. It depends on Longhorn device paths from `go-iscsi-helper`, common-libs exec interfaces, Kubernetes `mount-utils`, `fs` error matching, and logrus.

### Integration Points
Engine shutdown and frontend cleanup flows can call these helpers to release frozen filesystems before device teardown. Tests can inject fake executors and mounters through the function parameters.

### Risks
`fsfreeze` behavior is kernel/device dependent. A timeout on unfreeze may mean the kernel is still waiting for I/O errors, and the process may continue beyond the helper return. Error detection relies on the string `Invalid argument` for not-frozen state. Namespace assumptions depend on `/host` mount propagation.

### Test Signals
Tests should cover nil executor/mounter defaults, not-frozen errors, timeout errors, canonical mount cleanup, fallback mount scanning, empty volume/device names, and warning paths when mount-point checks fail.
