## sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/config.go

Purpose: adds `config` subcommands to the snapshotter daemon binary for inspecting effective and default configuration.

Important APIs/types/functions: `ConfigCommand`, with `dump` and `default` child commands.

Control flow: `dump` loads TOML through `config.NewConfigFromToml(cmd.String("config"))` and emits the parsed config as TOML. `default` calls `config.NewConfig()` and emits defaults.

State and persistence: reads config files but writes only to stdout; no state mutation.

Dependencies and integration: uses `pelletier/go-toml/v2`, `urfave/cli/v3`, containerd logging, and the config package.

Risks and test signals: on load error it calls `log.Fatal`, which exits rather than returning a normal CLI error. Main tests exercise env var override for config dump.
