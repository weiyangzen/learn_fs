# sources/cloud-native/cri-o/server/sandbox_update_resources_test.go

Purpose: Ginkgo tests for sandbox resource update lookup behavior.

Important APIs and functions: calls `sut.UpdatePodSandboxResources`.

Control flow: adds a container/sandbox for success, then calls the API with that ID; separately calls with invalid ID and expects an error.

State and persistence: in-memory sandbox setup only; NRI is inactive/no-op in normal test setup.

Dependencies and integration: CRI-O test framework and CRI update request types.

Risks: does not verify NRI payload conversion or plugin-side resource mutation.

Test signals: covers API success/no-op and NotFound behavior.
