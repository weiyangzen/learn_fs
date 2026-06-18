<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp_unix.go -->
# sources/cloud-native/containerd/core/mount/temp_unix.go

Purpose: Unix implementation for configuring and cleaning temporary mount directories.

Important APIs/types/functions: `SetTempMountLocation(root string)` and `CleanupTempMounts(flags int)`.

Control flow: `SetTempMountLocation` creates the directory, canonicalizes it, and assigns `tempMountLocation` so later prefix filtering works. `CleanupTempMounts` lists mountinfo entries under the temp location, sorts deepest first, unmounts each with `UnmountAll`, removes each mountpoint directory, and accumulates warnings while returning a fatal error only for mountinfo lookup failure.

State and persistence: updates package-global temp mount base and removes real temporary mounts/directories.

Dependencies and integration points: used by daemon startup/cleanup flows and idmapped overlay temporary remounts. Depends on `moby/sys/mountinfo`, `CanonicalizePath`, and platform unmount helpers.

Risks: warnings are non-fatal, so callers must inspect them to notice leaked mounts or directories. Prefix filtering depends on canonical temp path.

Test signals: no direct test in this subset, but recursive unmount behavior is covered in Linux mount tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp_unix.go -->
