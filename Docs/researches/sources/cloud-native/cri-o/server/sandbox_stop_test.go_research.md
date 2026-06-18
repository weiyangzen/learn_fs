# sources/cloud-native/cri-o/server/sandbox_stop_test.go

Purpose: Ginkgo tests for pod sandbox stop wrapper behavior.

Important APIs and functions: calls `sut.StopPodSandbox` with a prepared sandbox, invalid ID, and empty request.

Control flow: prepares a created sandbox and marks its network stopped, then verifies stop succeeds. Invalid IDs should succeed idempotently; empty IDs should error.

State and persistence: in-memory sandbox/container setup plus sandbox stopped/network-stopped flags.

Dependencies and integration: CRI-O test framework and CRI stop request types.

Risks: package describe name says `PodSandboxStatus`, likely copy-paste. Does not assert container stop, NRI, namespace, or log cleanup.

Test signals: protects CRI idempotency and empty-ID validation.
