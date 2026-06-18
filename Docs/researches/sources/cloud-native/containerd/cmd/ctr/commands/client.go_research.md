# sources/cloud-native/containerd/cmd/ctr/commands/client.go

Purpose: centralizes `ctr` command context creation and containerd client construction.

Important APIs/functions: `AppContext()` injects namespace, timeout, and optional `SOURCE_DATE_EPOCH`; `NewClient()` checks socket accessibility, creates a containerd client with connect timeout, creates app context, and emits server deprecation warnings unless suppressed.

Control flow: each command calls `NewClient()`, defers cancel, then uses the returned client/context. Deprecation warnings are fetched from the introspection service unless `CONTAINERD_SUPPRESS_DEPRECATION_WARNINGS` parses true.

State and persistence: reads environment variables `SOURCE_DATE_EPOCH` and `CONTAINERD_SUPPRESS_DEPRECATION_WARNINGS`; no writes.

Dependencies/integration: containerd client package, namespace package, epoch helper, logging, and OS socket stat.

Risks: `NewClient()` requires the socket path to exist before dialing, which can reject dialer-supported non-files if used unexpectedly. Deprecation checking adds an introspection RPC to most commands and only warns on failure.

Test signals: no local tests in this subset; behavior is widely used by command modules.
