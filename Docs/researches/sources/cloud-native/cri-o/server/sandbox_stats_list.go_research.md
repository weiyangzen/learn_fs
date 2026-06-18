# sources/cloud-native/cri-o/server/sandbox_stats_list.go

Purpose: implements CRI pod sandbox stats listing and streaming.

Important APIs and functions: `ListPodSandboxStats`, `StreamPodSandboxStats`, and `listPodSandboxStats`.

Control flow: optional stats filter is converted to a normal pod sandbox filter for ID/label matching, then `StatsForSandboxes` is called. Streaming chunks by `streamChunkSize`.

State and persistence: read-only over sandbox store and stats helpers.

Dependencies and integration: CRI stats list/stream APIs, sandbox filtering from `sandbox_list.go`, and CRI-O stats aggregation.

Risks: stats filter supports ID and labels here, not state; output includes whatever `StatsForSandboxes` returns for matching sandboxes.

Test signals: no direct tests in this subset.
