# sources/cloud-native/containerd/internal/fsmount/fsmount_linux.go

## Purpose
Wraps the Linux new mount API (`fsopen`, `fsconfig`, `fsmount`, `move_mount`) to mount filesystems while avoiding traditional `mount(2)` option string size limits.

## Important APIs, Types, And Functions
`Fsopen` opens a filesystem context. `SupportsFsmount` detects syscall availability. `Fsmount` configures source/options, creates a mount fd, and moves it to the target. Internal `mountAttrFlags` maps common options to `MOUNT_ATTR_*` flags.

## Control Flow
`Fsmount` opens a context, sets `ro` before source when present, configures key/value and flag options individually, calls `FsconfigCreate`, creates a detached mount, and moves it into place.

## State And Persistence
Creates kernel mount state at the target path. File descriptors are closed after use.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix` and containerd `core/mount.Mount`. It integrates with snapshotters or mount code needing large option lists.

## Risks
Linux 5.2+ and privileges are required. Option classification can mis-handle filesystem-specific options if they overlap with mount attribute names. Target path handling and mount cleanup are caller responsibilities.

## Test Signals
No direct tests in this subset. Coverage likely comes from mount integration tests on supporting kernels.
