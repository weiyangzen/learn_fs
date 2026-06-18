# sources/cloud-native/moby/integration/internal/requirement/requirement.go

Purpose: shared requirement helpers for conditionally running integration tests based on environment capabilities.

Important APIs and helpers: `HasHubConnectivity(t)` plus platform-specific functions implemented in companion files.

Control flow: `HasHubConnectivity` calls `testutil.CheckHubConnectivity`, logs the error through `t.Logf` when unavailable, and returns a boolean.

State and persistence: no persistent state; it performs network/environment probing.

Dependencies and integration: depends on Moby internal testutil connectivity checks and testing logging. It is intended for skip decisions in tests requiring Docker Hub.

Risks: connectivity checks can be flaky due to network conditions, proxy configuration, or registry availability. Returning bool leaves skip/fail policy to callers.

Test signals: helper-only; improves test gating for external registry dependencies.
