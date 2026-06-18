# sources/cloud-native/containers-storage/userns_unsupported.go

Purpose: non-Linux fallback for automatic user namespace support.

Important APIs and control flow: under `//go:build !linux`, defines `store.getAutoUserNS` with the same signature as Linux but always returns nil maps and an error saying user namespaces are unsupported.

State and persistence: no state or side effects.

Dependencies and integration: imports `idtools` and `types` only to satisfy the shared method signature. Ensures the storage package compiles on unsupported platforms while callers receive a clear runtime error.

Risks: the error is a new `errors.New` value rather than `types.ErrNotSupported`, so callers cannot use a shared sentinel unless they match strings or wrap at a higher layer.

Test signals: platform compile coverage and any non-Linux tests invoking auto-userns should verify graceful failure.
