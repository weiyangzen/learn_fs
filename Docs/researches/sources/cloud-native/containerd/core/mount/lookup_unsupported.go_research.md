# sources/cloud-native/containerd/core/mount/lookup_unsupported.go

Purpose: fallback implementation of `Lookup` for unsupported platforms.

Important APIs: `Lookup(dir string) (Info, error)` returns an error indicating lookup is not implemented for the current platform.

Control flow: no probing or state access.

State and persistence: none.

Dependencies and integration: provides build compatibility for platforms without mountinfo support.

Risks: callers must handle unsupported lookup on these platforms.

Test signals: no direct tests in subset.
