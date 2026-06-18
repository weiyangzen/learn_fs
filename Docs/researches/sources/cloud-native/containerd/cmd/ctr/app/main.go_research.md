# sources/cloud-native/containerd/cmd/ctr/app/main.go

Purpose: constructs the `ctr` CLI application and registers core administrative/debug commands.

Important APIs/functions: `extraCmds` extension slice, `init()` for gRPC log suppression and help/version flag customization, and `New()` for CLI app construction.

Control flow: `New()` sets app metadata, disables slice flag separator, enables bash completion, defines global flags (`debug`, `address`, `timeout`, `connect-timeout`, `namespace`), registers command modules, appends platform extra commands, and sets a `Before` hook that turns on debug logging.

State and persistence: global CLI flags influence later command contexts and client connections. No direct persistence.

Dependencies/integration: imports many `cmd/ctr/commands/*` packages for command registration, default address and namespace values, containerd logging, and version metadata.

Risks: `ctr` is explicitly unsupported/debug-oriented, so command compatibility is not guaranteed. Global `cli.VersionFlag`/`cli.HelpFlag` mutations affect the process-wide urfave/cli package.

Test signals: no local tests in this subset for app assembly.
