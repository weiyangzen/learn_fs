# sources/cloud-native/nydus-snapshotter/internal/flags/flags_test.go

Purpose: basic flag construction and parsing test.

Flow: applies all urfave/cli flags to a stdlib `flag.FlagSet`, parses `--config-path`, `--root`, and `--log-level`, and asserts values land in `Args`.

State/dependencies: pure in-memory flag parsing.

Integration points: protects backward-compatible `--config-path` alias for nydusd config.

Risks/signals: does not test bool count semantics for `--log-to-stdout`, version flag, address, daemon mode, fs driver, or snapshotter `--config`.
