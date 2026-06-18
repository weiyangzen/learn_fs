# sources/cloud-native/cri-o/server/sandbox_remove_test.go

Purpose: Ginkgo tests for sandbox removal error behavior.

Important APIs and functions: exercises `sut.RemovePodSandbox` on an uncreated sandbox and `sut.StopPodSandbox` with an empty ID.

Control flow: adds a sandbox and ID index entry without marking it created, then expects removal to fail.

State and persistence: in-memory sandbox and PodIDIndex changes only.

Dependencies and integration: CRI-O test framework and CRI stop/remove request types.

Risks: test name includes remove, but one case calls stop for empty ID; successful removal cleanup is not covered here.

Test signals: protects error semantics for not-created sandboxes and empty IDs.
