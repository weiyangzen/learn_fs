## sources/cloud-native/moby/daemon/libnetwork/osl/namespace_unsupported.go

Purpose: unsupported-platform namespace stub for non-Linux, non-Windows, non-FreeBSD builds.

Important APIs/types/functions: empty `Namespace`, no-op `Destroy`, and `GetSandboxForExternalKey` returning nils.

Control flow: no real behavior; it compiles references where OSL functionality is not implemented.

State and persistence behavior: none.

Dependencies and integration points: complements platform-specific files selected by build tags.

Risks: callers must not expect functional sandboxing on these platforms. Returning `(nil, nil)` can be hazardous if higher layers do not guard platform support.

Test signals: build-only coverage.
