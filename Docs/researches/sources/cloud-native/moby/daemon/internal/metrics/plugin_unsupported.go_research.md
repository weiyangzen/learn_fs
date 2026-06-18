<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/plugin_unsupported.go -->
# sources/cloud-native/moby/daemon/internal/metrics/plugin_unsupported.go

Purpose: provides Windows stubs for metrics plugin registration and cleanup.

Important APIs and types: `RegisterPlugin` and `CleanupPlugin`.

Control flow: both functions no-op; registration returns nil.

State and persistence: none.

Dependencies and integration: preserves cross-platform build compatibility for callers that register metrics plugins unconditionally.

Risks: callers may interpret nil as enabled metrics plugin support, while Windows behavior is silently disabled.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/plugin_unsupported.go -->
