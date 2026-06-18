# sources/cloud-native/containers-storage/pkg/mount/mounter_unsupported.go

Purpose: marks mount operations unsupported on platforms other than Linux and FreeBSD+cgo.

Important APIs, types, and functions: platform `mount`.

Control flow: immediately panics with `"Not implemented"`.

State and persistence: no state; no mount operation is attempted.

Dependencies and integration points: selected for `!linux && !(freebsd && cgo)`. High-level `Mount` and `ForceMount` will reach this implementation on unsupported platforms.

Risks and edge cases: runtime panic rather than returned error, so callers must platform-guard mount operations. This is unsuitable for graceful degradation unless wrapped.

Test signals: no direct tests; compile-time selection is the main signal.
