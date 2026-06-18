# sources/cloud-native/containerd/pkg/os/os_unix.go

Purpose: Unix symlink resolution implementation for `RealOS`.

Important APIs/types/functions: `RealOS.ResolveSymbolicLink(path)` calls `os.Lstat`, returns the path unchanged when it is not a symlink, and otherwise returns `filepath.EvalSymlinks(path)`.

Control flow: lstat first avoids resolving non-symlink paths unnecessarily. Symlink paths are fully evaluated through the standard library.

State/persistence: reads filesystem metadata only.

Dependencies/integration: build tag `!windows`; satisfies `OS.ResolveSymbolicLink` for Unix-like systems.

Risks: `EvalSymlinks` resolves the full path and may fail on missing intermediate components or permission issues. It is not scoped; callers needing scope containment should use `FollowSymlinkInScope`.

Test signals: platform tests should cover symlink and non-symlink paths, missing paths, and permission errors.
