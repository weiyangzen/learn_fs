# sources/cloud-native/moby/daemon/logger/plugin_unsupported.go

Purpose: non-Linux/non-FreeBSD fallback for plugin stream creation.

Important APIs/types/functions: `openPluginStream` returns an unsupported error.

Control flow/state/persistence: no persistence; always fails.

Dependencies/integration: selected by build tags to disable logging plugins on unsupported platforms.

Risks: callers must surface the error clearly when a plugin logger is requested.

Test signals: build tag coverage and platform builds.
