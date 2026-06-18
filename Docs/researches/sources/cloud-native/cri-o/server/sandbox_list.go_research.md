# sources/cloud-native/cri-o/server/sandbox_list.go

Purpose: implements CRI pod sandbox listing and streaming with filter support.

Important APIs and functions: `ListPodSandbox`, `StreamPodSandboxes`, `listPodSandboxes`, `filterSandboxList`, and `filterSandbox`.

Control flow: list filters in-memory sandboxes by optional ID, created-state, CRI state, and labels; then projects each sandbox's CRI object. Streaming chunks results by `streamChunkSize`.

State and persistence: read-only over sandbox store and pod ID index.

Dependencies and integration: Kubernetes CRI pod sandbox filters, Kubernetes field selectors for label matching, CRI-O sandbox store.

Risks: filtering is applied in both sandbox-object and CRI-object layers, which is redundant but defensive. Missing filtered IDs return an empty list instead of errors per CRI expectations.

Test signals: `sandbox_list_test.go` covers success, created-only filtering, listing without infra container, ID/state/label filters, and missing filtered IDs.
