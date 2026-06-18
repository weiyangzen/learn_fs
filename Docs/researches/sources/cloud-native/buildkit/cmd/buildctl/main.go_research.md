# Research: sources/cloud-native/buildkit/cmd/buildctl/main.go

Purpose: is the entrypoint for the `buildctl` CLI binary. It defines global flags, registers subcommands, initializes logging, tracing, profiling, version output, and central error handling.

Important APIs and flow: `init` sets exported product/version info and suppresses OTEL stdio errors. `main` computes default address from `BUILDKIT_HOST` or app defaults, defines global debug/address/TLS/timeout/wait/log flags, registers `du`, `prune`, `prune-histories`, `build`, `debug`, and `dial-stdio`, disables slice flag separators recursively, configures logrus in `Before`, attaches command tracing, attaches profiler flags, and runs the CLI. `handleErr` prints source locations, policy deny messages, and either stack-formatted or concise errors before exiting.

State and dependencies: process-global state includes logrus formatter/level, OTEL error handler, stack version info, and CLI metadata context. It imports connection helper packages for side effects.

Risks and test signals: global command initialization is central; mistakes affect every command. TLS and timeout flags feed common client resolution. Integration `testUsage` checks base/help success, while most command behavior is covered elsewhere.
