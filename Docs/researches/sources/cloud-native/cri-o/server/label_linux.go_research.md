# sources/cloud-native/cri-o/server/label_linux.go

Purpose: Linux SELinux relabel helper for paths used by volumes and mounts.

Important APIs and functions: `securityLabel(path, secLabel, shared, maybeRelabel)` optionally canonicalizes the desired label and skips relabel when the current top-level file label already matches, then calls `label.Relabel`.

Control flow: when `maybeRelabel` is true, the function tries to canonicalize and compare labels; failures are logged but do not stop relabel. `label.Relabel` errors are returned unless the platform reports `ENOTSUP`.

State and persistence: mutates filesystem SELinux labels recursively or shared according to the caller's `shared` flag. It reads current labels before deciding to skip.

Dependencies and integration: uses opencontainers SELinux APIs and Linux `unix.ENOTSUP`. Called by container/sandbox volume setup paths that need process and mount labels applied.

Risks: skip optimization only checks the top-level path, so callers must ensure that is enough for their relabel semantics. Logging canonicalization failures while continuing can hide malformed labels until `Relabel`.

Test signals: no direct test in this subset; behavior is likely exercised indirectly through container/sandbox mount setup tests elsewhere.
