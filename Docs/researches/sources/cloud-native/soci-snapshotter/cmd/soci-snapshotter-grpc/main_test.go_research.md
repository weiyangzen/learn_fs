## sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/main_test.go

Purpose: tests environment variable overrides for the daemon CLI.

Important APIs/types/functions: `TestEnvVarOverridesDefaultConfigPath`, `TestEnvVarOverridesDefaultLogLevel`, and `writeTestConfig`.

Control flow: first test writes a custom TOML, sets `SOCI_SNAPSHOTTER_CONFIG`, redirects stdout to a temp file, runs `config dump`, and reloads output to assert CRI path. Second test sets config/log/root/address env vars, starts app in a goroutine, waits briefly, and checks logrus level.

State and persistence: uses temp dirs/files and environment variables via `t.Setenv`.

Dependencies and integration: exercises `buildApp`, config loader/dumper, log-level flag source, and daemon startup enough to mutate global logrus level.

Risks and test signals: second test launches `app.Run` without synchronizing shutdown result, so failures can be hidden. It does not assert socket serving or cleanup.
