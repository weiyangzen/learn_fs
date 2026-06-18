# sources/cloud-native/containers-storage/pkg/mount/unmount_unsupported.go

Purpose: marks unmount unsupported on Windows.

Important APIs, types, and functions: platform `unmount`.

Control flow: immediately panics with `"Not implemented"`.

State and persistence: no state or unmount action occurs.

Dependencies and integration points: selected for Windows builds. High-level `Unmount` reaches this implementation unless guarded.

Risks and edge cases: panic-based unsupported behavior requires callers to avoid mount APIs on Windows.

Test signals: no direct tests; compile-time selection is the main signal.
