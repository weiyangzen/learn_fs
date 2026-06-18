# sources/cloud-native/moby/integration/internal/network/states.go

Purpose: polling predicate for network removal.

Important APIs and helpers: `IsRemoved(ctx, apiClient, networkID)` returns a gotest poll check.

Control flow: the predicate calls `NetworkInspect`. If the network is not found it returns success; any other error is a poll error; an existing network returns continue.

State and persistence: reads daemon network state only.

Dependencies and integration: depends on Moby network API client, containerd error classification, and gotest poll.

Risks: only distinguishes not-found from all other errors. It does not validate that dependent endpoints are gone beyond inspect failure.

Test signals: helper-only; used to wait for asynchronous network deletion.
