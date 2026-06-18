# sources/cloud-native/containerd/cmd/containerd/server/config/config_test.go

Purpose: validates daemon config loading, merging, imports, migration, and service config migration behavior.

Important APIs/functions tested: `migrations`, `mergeConfig()`, `resolveImports()`, `LoadConfig()`, `LoadConfigWithPlugins()`, `Config.Decode()`, `Config.MigrateConfig()`, `serviceMigrate()`, and `testMergeConfig()` helper.

Control flow: tests create temporary TOML files, load them into `Config`, assert merged/migrated output, and in some cases marshal plugin subtrees back to TOML to compare expected structure. `TestServiceMigrate` uses subtests to cover full migration, TTRPC default derivation, explicit UID/GID preservation, existing plugin config preservation, and empty config.

State and persistence: uses `t.TempDir()` and temporary config files. No repository state is mutated.

Dependencies/integration: uses `testify/assert`, `testify/require`, `pelletier/go-toml/v2`, containerd defaults/version, and `logtest`.

Risks covered: catches missing migration functions when config version advances; validates import circularity handling; prevents higher-version drop-ins from silently loading; protects sparse GRPC import merge semantics; ensures legacy service fields migrate to version 4 plugin blocks.

Test gaps: tests focus on config behavior, not daemon startup. Some assertions compare TOML formatting, which can be sensitive to encoder output changes.
