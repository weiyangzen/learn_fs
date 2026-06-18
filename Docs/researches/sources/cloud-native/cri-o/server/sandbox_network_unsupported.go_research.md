# sources/cloud-native/cri-o/server/sandbox_network_unsupported.go

Purpose: non-Linux/non-FreeBSD no-op network namespace hooks.

Important APIs and functions: `validateNetworkNamespace` returns nil and `cleanupNetns` logs a debug no-op.

Control flow: no platform-specific validation or cleanup occurs.

State and persistence: none.

Dependencies and integration: build-tag compatibility for shared network teardown logic.

Risks: unsupported platforms do not protect against invalid netns state here.

Test signals: compile-time coverage only.
