# Research: sources/cloud-native/buildkit/cmd/buildctl/common/common.go

Purpose: contains shared buildctl helpers for resolving daemon clients, TLS files, and Go-template output formats. It centralizes connection behavior used by build, debug, disk usage, prune, and history commands.

Important APIs and flow: `ResolveClient` derives TLS server name from `--addr` when omitted, rejects simultaneous `--tlsdir` and explicit TLS file flags, resolves cert files, attaches tracing client options when the command context has an active span, applies CA/client credentials, wraps the command context with an optional timeout, creates `client.New`, and optionally waits for backend readiness. `ParseTemplate` supports the `json` alias and a Docker-style `json` template function. `resolveTLSFilesFromDir` searches for PEM or cert-manager style names and fails if any CA/cert/key component is missing.

State and dependencies: no persistent state; it depends on CLI metadata, BuildKit client options, OpenTelemetry span context, URL parsing, templates, and filesystem stat calls for TLS material.

Risks and test signals: connection setup is security-sensitive because wrong server names or credential file selection can break TLS validation. `common_test.go` covers TLS directory resolution precedence and mixed file naming, while client resolution is covered indirectly by every integration CLI command.
