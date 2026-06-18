## sources/cloud-native/moby/daemon/libnetwork/osl/namespace_windows.go

Purpose: Windows namespace/sandbox stub for this OSL package.

Important APIs/types/functions: `GenerateKey` returns the container ID unchanged; empty `Namespace`; no-op `Destroy`; `NewSandbox` and `GetSandboxForExternalKey` return nils.

Control flow: no namespace creation or mutation occurs in this file.

State and persistence behavior: none. Windows networking is handled elsewhere or not through this Linux-style OSL implementation.

Dependencies and integration points: selected by Windows build tags to satisfy package references.

Risks: returning `(nil, nil)` requires callers to be platform-aware. Behavior differs from FreeBSD, which truncates keys, and Linux, which creates bind-mounted netns paths.

Test signals: build-only coverage in this subset.
