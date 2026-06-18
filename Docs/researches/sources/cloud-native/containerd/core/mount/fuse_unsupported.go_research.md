# sources/cloud-native/containerd/core/mount/fuse_unsupported.go

Purpose: non-Linux, non-Windows fallback for FUSE helpers.

Important APIs: `isFUSE` always returns false, and `unmountFUSE` returns a not-supported error string.

Control flow: no OS probing; this file is selected by build tags `!linux && !windows`.

State and persistence: none.

Dependencies and integration: keeps the mount package buildable on unsupported Unix-like platforms.

Risks: callers cannot perform FUSE-specific unmount behavior on these platforms through this helper.

Test signals: no direct tests in subset.
