# sources/cloud-native/cri-o/server/sandbox_status_test.go

Purpose: Ginkgo tests for pod sandbox status response content.

Important APIs and functions: calls `sut.PodSandboxStatus` with normal and verbose requests after preparing test containers/sandboxes.

Control flow: asserts success for a running infra container, checks first/additional IP mapping, expects error for empty sandbox ID, and verifies verbose `info` JSON contains OCI version and image.

State and persistence: in-memory sandbox/container state and spec mutations.

Dependencies and integration: CRI-O test framework, OCI container state/spec, CRI status request types.

Risks: does not cover evented PLEG container-status inclusion or spoofed infra verbose output.

Test signals: strong coverage for common status projection and multi-IP response behavior.
