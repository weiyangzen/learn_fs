# sources/cloud-native/containerd/core/mount/fuse_linux.go

Purpose: Linux-specific FUSE detection and FUSE unmount helper behavior.

Important APIs and data: constant `fuseSuperMagic`, `isFUSE`, and `unmountFUSE`.

Control flow: `isFUSE` calls `unix.Statfs` and compares filesystem type to the FUSE superblock magic, returning false on statfs errors. `unmountFUSE` tries `fusermount3 -u` and then `fusermount -u`, returning nil on first success or the last error.

State and persistence: no persistent state; executes external helper binaries.

Dependencies and integration: used by generic mount unmount code elsewhere in the mount package. Depends on Linux `statfs`, `os/exec`, and helper binaries.

Risks: absence of helper binaries or helper failure returns an error even if kernel unmount might otherwise work. `isFUSE` treats stat errors as non-FUSE, so callers must handle later unmount errors.

Test signals: no direct tests in subset.
