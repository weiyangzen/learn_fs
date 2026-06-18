# sources/cloud-native/cri-o/server/sandbox_stats.go

Purpose: implements CRI `PodSandboxStats` for a single sandbox.

Important APIs and functions: `PodSandboxStats` resolves the sandbox through `getPodSandboxFromRequest` and returns `s.StatsForSandbox(sb)`.

Control flow: lookup error propagates; otherwise response construction is direct.

State and persistence: read-only over sandbox store and stats providers.

Dependencies and integration: CRI stats API and CRI-O stats aggregation helpers.

Risks: error semantics mirror `getPodSandboxFromRequest`, so empty IDs and not-created sandboxes are errors.

Test signals: no direct tests in this subset.
