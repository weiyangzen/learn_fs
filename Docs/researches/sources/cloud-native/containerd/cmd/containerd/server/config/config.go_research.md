# sources/cloud-native/containerd/cmd/containerd/server/config/config.go

Purpose: defines containerd daemon configuration, TOML loading, imports, migration, merging, plugin config decoding, and disabled-plugin filtering.

Important APIs/types/functions: `Config` is the daemon config root; `StreamProcessor`, `GRPCConfig`, `TTRPCConfig`, `Debug`, `MetricsConfig`, `CgroupConfig`, and `ProxyPlugin` model config sections. `ValidateVersion()`, `MigrateConfig()`, `MigrateConfigTo()`, `v1MigratePluginName()`, `v1Migrate()`, `serviceMigrate()`, `Decode()`, `LoadConfig()`, `LoadConfigWithPlugins()`, `loadConfigFile()`, `resolveImports()`, `mergeConfig()`, `sliceTransformer`, and `V2DisabledFilter()` are the main APIs.

Control flow: loading starts with a pending queue seeded by the root config path. Each config is decoded with strict unknown-field logging fallback, optionally migrated from its version to the target `out.Version`, plugin-specific migrations run once per version step, config is merged into `out`, imports are resolved relative to the parent file or globbed, and circular imports are skipped via `loaded`. After all files, `ValidateVersion()` rejects too-new versions and short plugin names in disabled/required lists.

State and persistence: reads TOML files only. Merge behavior mutates the output `Config`: scalar zero values generally do not override non-zero values, slices append unique entries, plugin maps are merged by `mergo`, and `StreamProcessors`, `ProxyPlugins`, and `Timeouts` copy keys from later configs. Service migration moves legacy top-level GRPC/TTRPC/debug/metrics data into plugin config maps and clears migrated legacy fields.

Dependencies/integration: uses `pelletier/go-toml/v2` for strict/fallback decode, `mergo` for merge semantics, plugin registrations for config migration callbacks, containerd `version.ConfigVersion`, logging, and plugin URI filtering.

Risks: migration array length must track `version.ConfigVersion`. `LoadConfigWithPlugins()` uses root config version as the upper bound for drop-in config versions, so higher-version imports fail. Generic `map[string]any` plugin configs require careful type handling. `mergeConfig()` comments require updates when new map fields are added. `serviceMigrate()` has subtle compatibility behavior for deriving TTRPC from legacy GRPC.

Test signals: heavily covered by `config_test.go`: migration count, merge behavior, import resolution, unknown/default version behavior, plugin decode, CRI drop-in merge cases, service migration, and v3 TTRPC derivation.
