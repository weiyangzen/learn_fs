# sources/cloud-native/containerd/core/mount/loopback_handler_linux.go

Purpose: implements a mount manager handler for `loop` mounts by attaching a backing file to a loop device and tracking it through a symlink.

Important APIs and types: `LoopbackHandler`, `loopbackHandler`, `Mount`, and `Unmount`.

Control flow: `Mount` rejects non-`loop` mount types with `ErrNotImplemented`, sets up a loop device with autoclear enabled, creates a symlink from the loop device path to the manager mountpoint, then disables autoclear so the loop device remains active while tracked. It returns an `ActiveMount` with mount metadata and mountpoint. `Unmount` reads the symlink, opens the loop device, enables autoclear, removes the symlink, and if symlink removal fails attempts to disable autoclear again to prevent untracked reuse.

State and persistence: loop device kernel state plus a filesystem symlink at the mount manager path. `MountedAt` records activation time.

Dependencies and integration: depends on `SetupLoop`, `setLoopAutoclear`, errdefs, logging, and the mount manager `Handler` interface.

Risks: mount path symlink creation failure after loop setup relies on defer close/autoclear for cleanup. If symlink removal fails and resetting autoclear also fails, the loop device may be cleaned while still tracked. TODOs note readonly and direct IO options are not handled.

Test signals: no direct handler tests in subset; loop device primitives are covered by `losetup_linux_test.go`.
