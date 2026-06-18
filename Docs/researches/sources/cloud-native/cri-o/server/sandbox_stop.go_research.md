# sources/cloud-native/cri-o/server/sandbox_stop.go

Purpose: implements CRI `StopPodSandbox` wrapper and CRI-specific idempotent lookup behavior.

Important APIs and functions: `StopPodSandbox` resolves the requested sandbox and delegates to platform-specific `stopPodSandbox`.

Control flow: empty ID errors are returned. Not-created sandboxes return a clear error. Missing sandboxes return an empty successful response to satisfy CRI idempotency. Found sandboxes are stopped by platform code.

State and persistence: mostly read-only until delegation; platform implementation mutates runtime/network/sandbox state.

Dependencies and integration: CRI request/response types, sandbox ID lookup, platform-specific stop implementation.

Risks: missing sandbox success can hide unexpected index/store divergence, although it follows CRI expectations.

Test signals: `sandbox_stop_test.go` covers already-stopped behavior, missing sandbox idempotency, and empty ID error.
