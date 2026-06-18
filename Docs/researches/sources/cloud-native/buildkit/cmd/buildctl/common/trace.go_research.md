# Research: sources/cloud-native/buildkit/cmd/buildctl/common/trace.go

Purpose: attaches OpenTelemetry tracing to buildctl commands and stores the command context in root CLI metadata so other helpers can retrieve it consistently. It also delegates trace export over BuildKit client connections.

Important APIs and flow: `AttachAppContext` builds a base app context, creates a detected span exporter plus delegated exporter, wraps each top-level command `Before` hook to start a span named after the command, stores the span context under `Root().Metadata["context"]`, records errors in `ExitErrHandler`, ends the span in `After`, and shuts down the tracer provider with a short `exportTimeout`. `CommandContext` retrieves the context from CLI metadata.

State and dependencies: state is per-process CLI metadata plus an active span. It depends on BuildKit app context helpers, tracing detection, delegated exporter, OTEL SDK trace provider, and urfave/cli hooks.

Risks and test signals: `CommandContext` assumes metadata was initialized, so commands must go through `AttachAppContext`. The short 50 ms shutdown avoids hanging CLIs but can drop slow trace exports. There are no file-local tests; behavior is exercised indirectly by CLI execution.
