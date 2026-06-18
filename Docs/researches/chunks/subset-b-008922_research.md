# sources/storage-engines/tikv/src/config/mod.rs - chunk subset-b-008922 research

Chunk scope: lines 1-6602 of `sources/storage-engines/tikv/src/config/mod.rs`. This is chunk 1 of 2 for the TiKV server configuration module; the visible boundary ends inside the `#[cfg(test)] mod tests` body, so later tests and any tail behavior are cross-chunk material.

## Purpose

This chunk defines most of TiKV's top-level configuration model, validation pipeline, RocksDB/Titan/Raft Engine option construction, online configuration dispatch, persistence of last-effective configuration, and the start of the unit/integration tests for those behaviors. The module is the central bridge between serde/TOML configuration, `OnlineConfig` typed diffs, RocksDB/raft-engine runtime option APIs, raftstore/storage/coprocessor/server subconfigs, Prometheus metrics, and upgrade compatibility rules.

The top-level exported type is `TikvConfig`, which aggregates server, storage, raftstore, coprocessor, RocksDB, raftdb, raft-engine, readpool, backup, log backup, CDC, resolved-ts, resource control, quota, memory, in-memory-engine, logging, security, import, GC, pessimistic-transaction, and related subconfigs. The chunk also includes `ConfigController`, which applies online changes to registered module-specific `ConfigManager`s and optionally persists supported changes back to the config TOML.

## Important APIs, Types, and Functions

### RocksDB/Titan configuration

- `TitanCfConfig` controls Titan column-family options such as `min_blob_size`, blob compression, shared/separate blob cache, GC batch sizes, discardable ratio, blob run mode, and merge behavior. `build_opts` converts it into `RocksTitanDbOptions`; `validate` rejects deprecated `gc_merge_rewrite` and warns on deprecated `sample_ratio`.
- `TitanDbConfig` controls DB-level Titan options including enablement, directory, background GC, and obsolete-file purge period. It builds `RocksTitanDbOptions` and writes DB-level Titan metrics.
- `BackgroundJobLimits`, `get_background_job_limits_impl`, and `get_background_job_limits` derive default RocksDB background job, flush, subcompaction, and Titan GC thread limits from CPU quota and engine type. RaftKv2 deliberately uses fewer compaction threads for stability.
- `cf_config!` generates the shared CF config struct shape used by `DefaultCfConfig`, `WriteCfConfig`, `LockCfConfig`, `RaftCfConfig`, and `RaftDefaultCfConfig`. Generated fields cover block/table format, bloom/ribbon filters, compression, write buffers, L0 stall thresholds, compaction limits, compaction guard, checksums, TTL/periodic compaction, and nested Titan CF config.
- `build_cf_opt!` converts a CF config into `RocksCfOptions`, including block-based options, compression, write buffers, compaction guard SST partitioner, compaction thread limiter, TTL, periodic compaction, and write-stall thresholds.
- `write_into_cf_metrics!` exports the visible CF and Titan CF config state into `CONFIG_ROCKSDB_CF_GAUGE`.
- `CfResources` carries shared cache, per-CF compaction thread limiters, per-CF write buffer managers, and a `ForcePartitionRangeManager`.
- `DefaultCfConfig::build_opt`, `WriteCfConfig::build_opt`, `LockCfConfig::build_opt`, `RaftCfConfig::build_opt`, and `RaftDefaultCfConfig::build_opt` specialize generic CF options with collectors, prefix extractors, compaction filters, Titan options, and write-buffer managers. Notable integrations include range/MVCC/raw-MVCC/TTL property collectors, `WriteCompactionFilterFactory`, `RawCompactionFilterFactory`, `TtlCompactionFilterFactory`, and `RangeCompactionFilterFactory`.
- `DbConfig` models the KV RocksDB instance, including WAL, background jobs, rate limiter, direct I/O, pipelined/multi-batch/unordered writes, write buffer manager, and all four CF configs.
- `DbConfig::optimize_for` fills engine-specific defaults. For RaftKv it enables concurrent memtable writes, sets WAL/stat defaults, compaction guard defaults, and lock CF write buffer size. For RaftKv2 it disables multi-batch/concurrent memtable writes by default, sets a capped global write buffer limit, disables write stalls, forces low compaction concurrency, and configures lock CF limits.
- `DbConfig::build_resources`, `build_opt`, `build_cf_resources`, and `build_cf_opts` allocate rate limiters, write-buffer managers, statistics, DB options, and CF options for the target engine.
- `DbConfig::validate` enforces nested CF/Titan validity, rejects raft CF write buffer manager, rejects write CF Titan writes, rejects unordered-write/Titan combinations, normalizes unordered write by disabling pipelined write, and caps online background job fields by CPU quota.
- `RaftDbConfig` and `RaftDefaultCfConfig` model the legacy raft RocksDB instance. Raft DB defaults use a separate lower background job profile, force raft-specific logger/event listener behavior, and only expose the default CF.
- `RaftEngineConfig` wraps `raft_log_engine::RaftEngineConfig`. `validate` sanitizes and fills a memory limit at 15% of system memory if unset; `optimize_for` adapts batch compression threshold for async raftstore IO unless the user customized that threshold.

### Read pools and service-level configs

- `UnifiedReadPoolConfig` validates min/max threads, stack size, tasks per worker, CPU threshold, and a CPU-quota-derived max thread cap. The default uses about 80% of available CPU with a minimum of 4 workers.
- `readpool_config!` generates separate storage and coprocessor read-pool configs with high/normal/low pools, unified-pool inference, yatp config conversion, and validation. `use_unified_pool` defaults to true only when the module-specific config is still at default values.
- `ReadPoolConfig` coordinates unified/storage/coprocessor validation and exposes `is_unified_pool_enabled` and `adjust_use_unified_pool`.
- `BackupConfig` validates and normalizes backup thread count, batch size, and S3 multipart size. Defaults scale backup threads with CPU and derive SST size from coprocessor region size.
- `BackupStreamConfig` validates log-backup flush/min-TS intervals, initial scan concurrency/rate limit, thread count, and S3 multipart size. Defaults derive temp-file and pending-memory quotas from system memory.
- `CdcConfig` validates/normalizes CDC intervals, scan thread/concurrency relationships, concurrency limits, TS filter ratio, memory quotas, and disables hibernate compatibility for raftstore v2.
- `ResolvedTsConfig` validates nonzero advance interval and scan-lock pool size.
- `LogConfig` plus `LogLevel` wrap slog levels with serde and `ConfigValue` conversion; `LogConfigManager` applies online `log.level` changes through `set_log_level`.
- `MemoryConfig` initializes heap profiling and thread-exclusive arenas; `MemoryConfigManager` toggles profiling and sample rate online.
- `QuotaConfig` validates bounded maximum delay duration.

### Top-level config and validation

- `TikvConfig` is the main server config aggregate. It includes deprecated top-level log fields for compatibility, runtime-only/skipped fields, and many `#[online_config(submodule)]` modules.
- `infer_raft_db_path`, `infer_raft_engine_path`, and `infer_kv_engine_path` canonicalize storage-derived engine directories.
- `TikvConfig::validate` is the key control path:
  - Initializes `cfg_path` to `storage.data_dir/last_tikv.toml` if unset.
  - Canonicalizes raft DB and raft-engine paths, inheriting raft-engine path from explicitly configured raftdb path for upgrade compatibility.
  - Fills log-backup temp path under storage data dir.
  - Rejects conflicting KV DB, raft DB, raft-engine, WAL, and Titan paths.
  - Detects KV data existence with either RocksDB `CURRENT` state for RaftKv or `tablets` dir for RaftKv2.
  - Runs `RaftDataStateMachine` validation to ensure legal raftdb/raft-engine state combinations.
  - Calls optimization hooks for RocksDB, coprocessor, split, raftstore, server, raft-engine, and block cache capacity.
  - Enforces RaftKv2-only constraints: raft log engine enabled, recovery threads minimum, purge threshold at least twice RocksDB write buffer limit, Titan disabled, compatible learner disabled, and no delete range.
  - Checks grpc keepalive against twice raft heartbeat interval and warns on CDC/hibernate-region incompatibility.
  - Integrates storage flow control with RocksDB write-stall settings by disabling write stall and clamping/filling L0 stop/slowdown and pending compaction thresholds across KV and raft CFs.
  - Calculates or validates `memory_usage_limit`, then rejects block cache plus write buffer limits that exceed it.
  - Validates every submodule, in-memory-engine compatibility, compaction-filter requirement for in-memory cross-check, and TTL/Titan incompatibility.
- `logger_compatible_adjust` migrates deprecated top-level log fields into the nested `log` config before logger initialization.
- `optional_default_cfg_adjust_with` handles optional Titan defaults after validation. It inherits Titan enablement and min blob size from the last persisted config when appropriate, enables Titan by default for new RaftKv clusters, disables it for existing non-Titan/TTL/RaftKv2 setups, and always sets RaftKv2 Titan disabled.
- `compatible_adjust` migrates deprecated raftstore region-size fields into coprocessor settings, inherits region size defaults from last config when not explicitly set, migrates deprecated endpoint readpool fields, handles old shared block-cache CF sizes, clamps backup SST size relative to region size, clears deprecated RocksDB `auto_tuned`, and adjusts unified readpool usage.
- `check_critical_cfg_with` rejects unsafe changes from last persisted config: storage data dir, KV WAL dir, raft DB path/WAL dir, raft-engine dir when raft-engine data exists, TTL enablement changes within API v1/v1ttl, and persisted RocksDB format versions above 5.
- `from_file`, `write_to_file`, `with_tmp`, and `build_shared_rocks_env` provide TOML load/save/test-config/shared-env helpers.

### Persistence and online update support

- `validate_and_persist_config` loads `last_tikv.toml`, normalizes/validates it, applies compatibility adjustments to current config, validates current config, fills optional defaults, checks critical config deltas, and persists the current effective config when requested.
- `get_last_config` loads `LAST_CONFIG_FILE` from the storage data dir and panics on malformed auto-generated config.
- `persist_config` writes `last_tikv.toml` atomically through `tmp_tikv.toml`, skips rewriting when content is unchanged, and creates the storage dir if missing.
- `write_config` atomically updates an arbitrary config file path using `tmp_tikv.toml` in the same directory.
- `to_flatten_config_info` serializes current and default config to JSON and produces a flattened list of config names/defaults/values-in-file. `server.labels` is intentionally not recursively flattened because it is a map.
- `TIKVCONFIG_TYPED` caches the `OnlineConfig` typed tree from defaults.
- `serde_to_online_config` maps external config keys into online-config field names, including `raftstore` to `raft_store`, kebab to underscore, and old raftstore pool-size keys into `store_batch_system` / `apply_batch_system`.
- `to_config_change` parses string-keyed online changes into typed `ConfigChange`, rejecting unknown, skipped, nested-too-deep, and type-invalid changes.
- `to_change_value` parses durations, sizes, integers, booleans, strings, floats, and schedules according to the typed default.
- `to_toml_encode` decides which string values need TOML quoting before persistence, especially sizes, durations, and strings.
- `Module` maps online-config module names to manager keys. Visible variants include readpool, server, metric, raftstore, coprocessor, pd, rocksdb, raftdb, raft-engine, in-memory-engine, storage, security, import, backup, log backup, pessimistic txn, GC, split, CDC, resolved-ts, resource-metering/control, quota, log, memory, and unknown.
- `ConfigController` owns an `Arc<RwLock<ConfigInner>>` with current config and registered module managers. `update` and `update_without_persist` parse changes then call `update_impl`; `update_from_toml_file` diffs a config file against current state. `update_impl` validates the candidate config first, dispatches module diffs to registered managers, rolls current state forward for already-dispatched partial success if a later dispatch fails, updates current state, and persists original user changes through `TomlWriter`/`write_config` when requested. `get_engine_type` returns `partitioned-raft-kv` for RaftKv2 and `raft-kv` otherwise.
- `DbConfigManger<D>` applies online RocksDB changes to a `ConfigurableDb`. It validates legal CF names by DB type, translates nested Titan CF changes into RocksDB option names, rejects online shared block-cache-size changes in the RocksDB module, only allows CF write-buffer-limit for lock CF, updates DB rate limiter/auto-tuning/write-buffer/background-job/subcompaction settings through dedicated APIs, and writes numeric/boolean CF updates into config metrics.

## Control Flow and State Behavior

Startup/config-file flow is: load TOML into `TikvConfig`, call `logger_compatible_adjust` early if needed, call `validate_and_persist_config`, load last persisted effective config if present, perform compatibility adjustment, validate/optimize the current config, fill optional Titan defaults based on existing data and last config, compare critical paths/settings against last config, then atomically persist the effective `last_tikv.toml`.

Runtime online-update flow is: string changes enter `ConfigController::update`, keys are normalized and typed via `to_config_change`, the candidate config is updated and validated, the resulting diff is dispatched per submodule, current in-memory state is updated, and supported changes are written back to the config file. Module-specific side effects are handled by registered managers, for example RocksDB option mutation, storage scheduler updates, log level changes, memory profiling toggles, and resolved-ts mock manager dispatch in tests.

RocksDB option construction is staged. `DbConfig::optimize_for` fills engine-specific defaults, `build_resources` creates shared DB resources, `build_opt` converts DB-level fields to `RocksDbOptions`, `build_cf_resources` creates cache/limiters/write-buffer managers for CFs, and `build_cf_opts` creates named CF option vectors. CF builds compose generic table/compaction/write-buffer settings with per-CF prefix extractors, collectors, and compaction filters.

Persistence is file-system stateful. `last_tikv.toml` records the effective config used by the last run. It is compared during later startup to reject unsafe data-location/API/format changes and to inherit optional defaults that are dangerous to recalculate blindly during upgrades. Writes use temp-file plus `fs::rename`, and `persist_config` avoids touching mtime when serialized content is unchanged.

## Dependencies and Integration Points

This chunk integrates heavily with:

- `engine_rocks` for RocksDB/Titan option types, raw RocksDB APIs, rate limiter, env, cache, write-buffer manager, statistics, collectors, compaction filters, event listeners, and loggers.
- `engine_traits` CF constants and option traits.
- `raft_log_engine` for raw raft-engine config and size types.
- `raftstore` config, split config, compaction guard, region info access, and `RaftDataStateMachine`.
- `storage::config` for storage engine type, block cache, flow control, API version, and data dir defaults.
- `server` config, GC/TTL compaction filters, lock manager config, and Prometheus gauges.
- `online_config` derive/runtime types for typed diffs and config manager dispatch.
- `tikv_util::config` readable size/duration/schedule, TOML writer, path canonicalization, quota and system memory/CPU utilities.
- `file_system::IoRateLimiter`, `encryption_export::DataKeyManager`, `pd_client::Config`, security/import/resource-metering/resource-control/causal-ts/in-memory-engine configs.
- Test-only integrations with `TestStorageBuilder`, RocksDB engine creation, raft log engine creation, storage config manager, flow controller, mock lock manager, and scheduler pool inspection.

## Risks and Edge Cases

- `ConfigController::update_impl` dispatches managers sequentially and updates current config with already-dispatched `to_update` if a later manager fails. This avoids double-dispatch on retry but can leave a partially applied runtime state relative to the original request; callers need to handle errors with that behavior in mind.
- Online RocksDB updates flatten nested Titan CF changes into RocksDB option names and stringify sizes/durations to raw numeric seconds/bytes. A mismatch between RocksDB option naming and `OnlineConfig` field naming can make an apparently valid config fail at runtime.
- Shared block cache size cannot be changed through RocksDB CF `block-cache-size`; it must be changed through `storage.block-cache.capacity`. The manager rejects this explicitly.
- Optional Titan defaults depend on existing KV data, Titan blob directory contents, last persisted config, and TTL/API/engine mode. Incorrect data-existence detection could enable/disable Titan unexpectedly.
- Critical config checks intentionally block storage/WAL/raft path changes and TTL flips for existing API v1/v1ttl instances. Operational migrations must arrange data movement before changing these settings.
- RaftKv2 has stricter constraints: no configured RocksDB WAL dir, raft log engine required, Titan unsupported, delete range unsupported, adjusted recovery/purge settings, and different memory/block-cache/write-buffer assumptions.
- Flow control mutates RocksDB stall settings during validation, including defaulting unset `level0_stop_writes_trigger` to the flow-control L0 threshold even when flow control config is represented by a disabled default object. This means validation can fill previously unset options.
- Memory validation is cross-field: block cache capacity plus RocksDB write buffer limit must not exceed `memory_usage_limit`. Defaults are derived from system quota, so tests and deployments can vary by cgroup/host memory.
- `get_last_config` panics if `last_tikv.toml` exists but cannot deserialize; startup recovery around corrupted auto-generated config is intentionally strict.
- `LogLevel::try_from` panics if passed a non-string `ConfigValue`; callers rely on typed online-config validation before conversion.
- The visible chunk ends mid-test module, so some test coverage for quota, server, endpoint, config templates, flow control, and in-memory engine is likely in the next chunk.

## Test Signals Visible in This Chunk

The chunk contains focused unit/integration tests through the beginning of `test_change_store_scheduler_worker_pool_size`:

- `unified_read_pool_tests` and generated readpool tests validate thread-count, stack-size, tasks-per-worker, max-thread CPU cap, CPU threshold, unified-pool bypass behavior, and partial unified pool rules.
- `readpool_tests` checks disabled/enabled/partially-unified readpool validation behavior.
- `test_check_critical_cfg_with` covers storage data dir, RocksDB WAL dir, raftdb WAL/path, raft-engine path, API v1/v1ttl TTL changes, raft-engine/raftdb upgrade/downgrade data-state combinations, and format/path safety.
- `test_last_cfg_modified`, `test_persist_cfg`, and `test_create_parent_dir_if_missing` cover atomic persistence, no-op persistence when content is unchanged, reading persisted WAL and coprocessor settings, and parent directory creation.
- `test_flatten_cfg` verifies flattened config output, including map handling for `server.labels` and non-default value reporting.
- `test_keepalive_check`, `test_illegal_backupstream_config_parm`, `test_block_size`, and `test_rocks_rate_limit_zero` cover grpc keepalive threshold, log-backup initial scan rate minimum, CF block-size max, and disabled RocksDB rate limiter.
- `test_parse_log_level` covers serde names, compatibility aliases, and invalid log levels.
- `test_write_metrics` verifies RocksDB DB/CF and raftstore config gauges for selected fields.
- `test_to_config_change` and `test_to_toml_encode` cover typed online parsing, key normalization, invalid keys/types/skipped fields, and TOML quoting of durations/sizes/strings.
- `new_engines` test helper constructs RocksDB, raft log engine, storage, flow controller, and registers RocksDB/storage config managers for online update tests.
- `test_change_resolved_ts_config` verifies unsupported resolved-ts fields fail, supported interval changes dispatch, and invalid zero duration is rejected without changing the local test config.
- `test_change_rocksdb_config`, `test_change_rate_limiter_auto_tuned`, and `test_change_shared_block_cache` verify online DB/CF background job, rate limiter, write-buffer, auto-tuned limiter, CF write-buffer-size, default CF compaction options, and shared block-cache update paths.
- `test_change_log_config` verifies online log level mutation and invalid-level rollback.
- `test_change_memory_config_ifdef_malloc_conf` is feature-gated/ignored and covers heap profiling toggles and sample-rate parsing.
- `test_dispatch_titan_blob_run_mode_config`, `test_update_titan_blob_run_mode_config`, and `test_titan_config_compatible_upgrade` verify Titan blob run mode formatting/parsing and startup compatibility across disabled, enabled, newly-created, and restart scenarios.
- `test_change_ttl_check_poll_interval` checks online storage TTL checker dispatch.
- `test_change_store_scheduler_worker_pool_size` begins at the chunk tail and verifies scheduler pool scaling rejects zero/too-large values and preserves old pool sizes on failure; its full body continues beyond this chunk.

## Cross-Chunk Notes

Chunk 2 starts at line 6603, inside the test module. The final per-file merge should reconcile additional tests after `test_change_store_scheduler_worker_pool_size`, especially any coverage for quota config, server/coprocessor endpoint updates, compatibility adjustment, config template validation, compaction guard, flow control, percentage values, WAL validation, CDC, module mapping, in-memory engine, and other tail-only cases.
