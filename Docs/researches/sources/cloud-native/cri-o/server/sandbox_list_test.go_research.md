# sources/cloud-native/cri-o/server/sandbox_list_test.go

Purpose: Ginkgo tests for `ListPodSandbox` filtering and created-state behavior.

Important APIs and functions: exercises `sut.ListPodSandbox`, sandbox store mutation, `LoadSandbox`, and PodIDIndex-driven filtering.

Control flow: prepares sandboxes directly or through mocked manifest/state loading, then asserts returned item counts for unfiltered and filtered calls.

State and persistence: mostly in-memory, with helper-created dummy state for loaded sandbox tests.

Dependencies and integration: CRI-O test framework, OCI container state, runtime-spec status, CRI filters.

Risks: does not test streaming chunk behavior.

Test signals: strong coverage for the list path's key CRI semantics: skip uncreated sandboxes, allow created sandboxes without infra container, and treat missing filter IDs as empty results.
