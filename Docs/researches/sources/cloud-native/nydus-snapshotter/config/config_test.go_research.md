# sources/cloud-native/nydus-snapshotter/config/config_test.go

Purpose: unit tests for snapshotter config loading, overrides, defaults, and processing.

Flow: loads `misc/snapshotter/config.toml` and compares a full expected struct, verifies CLI root/log-to-stdout precedence, checks mergo default merge behavior, verifies derived log/cache dirs, and asserts overly long root path validation fails.

State/dependencies: reads example config from repo and may look up default binaries through `FillUpWithDefaults`.

Integration points: protects the packaged config file contract and CLI/TOML precedence.

Risks/signals: full-struct equality is sensitive to config default changes. Validation tests are selective and do not cover invalid fs drivers, auth conflict, or mirror dir errors here.
