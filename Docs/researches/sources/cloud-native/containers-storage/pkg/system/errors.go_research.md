# sources/cloud-native/containers-storage/pkg/system/errors.go

Purpose: defines a shared unsupported-platform error for system helpers.

Important APIs, types, and functions: `ErrNotSupportedPlatform`.

Control flow: none beyond package variable initialization.

State and persistence: no persistence.

Dependencies and integration points: depends on `errors`. Used by unsupported extattr and meminfo implementations.

Risks and edge cases: callers should compare with `errors.Is` only if wrapping is added elsewhere; this file exposes a sentinel error.

Test signals: no direct tests in requested files.
