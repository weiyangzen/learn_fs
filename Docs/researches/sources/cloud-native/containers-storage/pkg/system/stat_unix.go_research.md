# sources/cloud-native/containers-storage/pkg/system/stat_unix.go

Purpose: Unix implementation of the package-neutral file stat abstraction.

Important APIs/types/functions: defines `StatT` with mode, uid, gid, rdev, size, mtime, dev, and embedded `platformStatT`; accessors `Mode`, `UID`, `GID`, `Rdev`, `Size`, `Mtim`, `Dev`, `IsDir`; and functions `Stat` and `Fstat`.

Control flow: `Stat` and `Fstat` call `syscall.Stat`/`Fstat`, wrap syscall failures in `os.PathError`, and delegate platform-specific field conversion to `fromStatT`.

State/persistence: read-only filesystem metadata snapshots.

Dependencies/integration: used across storage for ownership, size, device, and directory checks; platform conversion files supply syscall field mapping.

Risks: `Stat` follows symlinks rather than using `Lstat`. The abstraction has platform-dependent completeness, especially `Dev` and `Flags`.

Test signals: shared tests cover conversion of UID, GID, Rdev and platform mode/time; callers should also test symlink-specific needs separately.
