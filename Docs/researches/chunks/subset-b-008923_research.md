# sources/storage-engines/tikv/src/config/mod.rs lines 6603-8326

## Chunk Scope

This chunk is the tail of the `config::tests` module for TiKV's central configuration code. It starts at the end of the store pool-size test and then exercises dynamic config updates, config validation, compatibility adjustment, config-template drift checks, WAL directory safety, engine-specific defaults, CDC compatibility, online-config key mapping, flow-control rewrites, and in-memory engine validation.

The researched source span is `sources/storage-engines/tikv/src/config/mod.rs:6603-8326`. The production definitions for the config structs and managers appear earlier in the same file and related modules; this chunk is important because it documents the intended behavior through tests.

## Purpose

The chunk protects TiKV's configuration contract across startup validation, persisted last-config compatibility, and live configuration mutation. It verifies that user-facing TOML keys deserialize cleanly, that compatibility shims remain idempotent, that generated defaults match the shipped config template, and that online config updates reach the runtime components they control.

The tests also encode several operational safety rules:

- storage scheduler memory quota must reject malformed sizes and clamp `0B` to the pending write threshold;
- quota limiter updates must immediately affect foreground/background CPU and bandwidth delay calculations;
- server config changes must update the `VersionTrack<ServerConfig>` and forward endpoint settings to the coprocessor manager;
- KV and raft RocksDB/WAL paths must not overlap unless raft-engine replaces raft RocksDB;
- flow-control thresholds may rewrite RocksDB write-stall options to keep the flow controller consistent;
- API-version and TTL combinations constrain Titan and in-memory engine support.

## Important APIs, Types, and Test Helpers

- `TikvConfig::with_tmp`, `TikvConfig::default`, `TikvConfig::from_file`, `TikvConfig::validate`, and `TikvConfig::compatible_adjust` are the main config lifecycle APIs under test. The tests cover deserialization, computed defaults, persisted config inheritance, and final validation.
- `ConfigController::new`, `ConfigController::register`, `ConfigController::update_config`, and `ConfigController::get_current` are exercised for online updates. The tests register concrete managers for `Module::Quota`, `Module::Server`, and `Module::InMemoryEngine`.
- `QuotaLimiter`, `QuotaLimitConfigManager`, and `QuotaLimiter::consume_sample` prove that config-controller updates are not just reflected in the stored config but also change runtime limiter behavior and delay caps.
- `ServerConfigManager`, `VersionTrack<ServerConfig>`, `ResourceQuota`, `MockCfgManager`, and `dummy_scheduler` are used to validate live server config publication and forwarding of endpoint memory quota changes to the coprocessor endpoint layer.
- `new_engines::<ApiV1>` builds a temporary TiKV storage stack with RocksDB, a config controller, and flow controller so tests can inspect scheduler memory quota, RocksDB CF options, and flow-controller state after validation and live updates.
- `build_cf_opt!`, `DefaultCfConfig`, `Cache::new_lru_cache`, `LRUCacheOptions`, `MockRegionInfoProvider`, and `ConcurrentTaskLimiter` test how compaction-guard config transforms into RocksDB column-family options.
- `ReadableSize`, `ReadableSizeOrPercent`, `ReadableDuration`, `RaftEngineReadableSize`, `SysQuota`, `GIB`, and `Duration` are the user-facing typed config wrappers used for parsing, validation, computed defaults, and exact expected values.
- `EngineType::{RaftKv, RaftKv2}` drives many conditional defaults: endpoint request timeout, raft-engine defaults, region split size, split thresholds, background-job limits, CDC hibernate compatibility, and raftstore-v2 learner behavior.
- `must_no_unknown_key` uses `serde_ignored` over `toml::Deserializer` to assert that sample TOML snippets and the config template do not contain superfluous keys.
- `serde_to_online_config` maps external online-config names such as `raftstore.store-pool-size` to internal serde paths such as `raft_store.store_batch_system.pool_size`.

## Control Flow and Behavioral Coverage

The dynamic-update tests follow a common pattern: construct a valid `TikvConfig`, register a config manager with `ConfigController`, issue `update_config(path, value)`, then assert both the controller's current config and the target runtime object changed.

- `test_change_store_scheduler_memory_quota` builds real engines, obtains the storage scheduler, and updates `storage.memory-quota`. Invalid duration-like input (`11h`) must fail; `0B` must resolve to `scheduler_pending_write_threshold`; normal byte values become the scheduler's memory quota capacity.
- `test_change_quota_config` registers `QuotaLimitConfigManager` and updates foreground/background CPU time, read/write bandwidth, max delay duration, and `enable-auto-tune`. It consumes samples after updates to verify calculated delays, including a rejected `213504d` value that exceeds the `u64` nanosecond duration boundary.
- `test_change_server_config`, `test_endpoint_config`, and `test_change_coprocessor_endpoint_config` cover server online updates, default endpoint request timeout selection (`60s` for raft-kv, `1800s` for partitioned raft-kv), explicit override behavior, and forwarding `server.end-point-memory-quota` to a coprocessor endpoint config manager.
- `test_compatible_adjust_validate_equal` proves repeated `compatible_adjust(None)` plus `validate()` calls are idempotent.
- `test_readpool_compatible_adjust_config` proves readpool storage/coprocessor configs default to unified pool only when legacy per-pool fields are absent.
- `test_unrecognized_config_keys`, `test_config_template_no_superfluous_keys`, and `must_no_unknown_key` protect TOML schema hygiene and expected ignored-key reporting.
- `test_raft_engine_dir` verifies enabling raft-engine derives its directory from `storage.data_dir/raft-engine` when unset.
- `test_compaction_guard` verifies compaction guard leaves `target_file_size_base` unchanged when disabled or missing region info, but when enabled with a provider it sets RocksDB target file size to `compaction_guard_max_output_file_size`.
- `test_validate_tikv_config` covers validation side effects: region split check diff override, memory usage limit rejection above cgroup/system max, memory usage fallback from block cache, raftstore-v2 compatible learner disabling, ribbon filter requiring RocksDB format version >= 5, and Titan rejection with TTL on API v2.
- `test_config_percentage_values` verifies percentage strings for `storage.block-cache.capacity` and `memory-usage-limit`, rejects float syntax, and confirms full validation with percentage-derived sizes.
- `test_validate_tikv_wal_config` constructs overlapping KV/raft DB and WAL paths and validates which combinations are rejected under RocksDB raft storage and which become acceptable when raft-engine is enabled.
- `test_background_job_limits` locks down CPU-count and engine-dependent background job defaults for KV RocksDB and raft RocksDB.
- `test_config_template_is_valid` and `test_config_template_matches_default` strip comments from `etc/config-template.toml`, deserialize it, validate it, and compare it to `TikvConfig::default()` after normalizing environment-derived and post-validation computed fields.
- `test_region_size_config` and `test_inherit_region_size_config` cover raft-kv vs raft-kv2 region split defaults, split detector thresholds, region bucket enablement, and selective inheritance of region size/key settings from `LAST_CONFIG_FILE`.
- `test_compatibility_with_old_config_template` fetches the upstream master config template and verifies deserialization, tolerating timeout but panicking on other download failures.
- `test_cdc` accepts deprecated/zero CDC values, adjusts incremental scan concurrency limit upward when configured as zero, and disables `hibernate_regions_compatible` under partitioned raft-kv.
- `test_module_from_str` fixes module-name parsing, including unknown names preserving their string.
- `test_numeric_enum_serializing` supports numeric and string enum parsing for RocksDB compaction style, serializes back numerically, rejects invalid enum values through panic recovery, and verifies DB rate limiter mode serialization.
- `test_flow_control` and the three override tests verify validated flow-control settings rewrite RocksDB default CF stall options only when enabled and only when user/default limits exceed flow-control thresholds, while live toggles update RocksDB `disable_write_stall` and the `flow_controller.enabled()` flag.
- `test_in_memory_engine_and_api_version` verifies in-memory engine TOML validity, rejects enabled in-memory engine with TTL on API v1 or v2, and allows those API/TTL settings when the in-memory engine is disabled.
- `test_in_memory_engine_change_config` registers `InMemoryEngineConfigManager` and verifies online updates for capacity, eviction threshold, stop-load threshold, MVCC amplification threshold, GC interval, and enable flag through both kebab-case and snake-case module names.

## State and Persistence Behavior

Most tests operate on in-memory config values, but several explicitly cover persisted state:

- `validate_and_persist_config(&mut cfg, true)` writes the last validated config under `LAST_CONFIG_FILE` in the temporary `storage.data_dir`. Later `TikvConfig::from_file` loads it so `compatible_adjust(Some(&cfg_from_file))` can inherit only region sizing/key settings, not unrelated raftstore settings such as `raft_entry_max_size`.
- `test_raft_engine_dir` and `test_validate_tikv_wal_config` validate path canonicalization and directory layout rules before TiKV opens storage engines. These rules prevent data/WAL overlap that could corrupt KV and raft RocksDB state.
- `ConfigController` keeps an authoritative current `TikvConfig` snapshot while registered managers update runtime state. Tests compare both `get_current()` and manager-owned state (`VersionTrack`, scheduler capacity, `QuotaLimiter`, RocksDB options, and flow controller flags) to catch partial update bugs.
- `test_config_template_matches_default` normalizes fields whose effective defaults are computed after deserialization or depend on environment resources: thread counts, memory quotas, background jobs, block cache/memory limits, raft-engine memory, compaction-guard options, flow-control-related RocksDB thresholds, ribbon filters, CF TTL/periodic compaction, format versions, and Titan defaults.

## Dependencies and Integration Points

This test chunk integrates TiKV config with several subsystems:

- storage engine bootstrap through `new_engines::<ApiV1>`, RocksDB option inspection, raft-engine path derivation, and raft/KV WAL validation;
- runtime config management through `ConfigController`, module registration, per-module config managers, and `serde_to_online_config` key normalization;
- quota enforcement through `QuotaLimiter` delay calculations for foreground and background request classes;
- server and coprocessor endpoint config through `ServerConfigManager`, `VersionTrack`, `ResourceQuota`, and a mock coprocessor manager receiving changed fields;
- readpool, raftstore, coprocessor split, split-check, CDC, Titan, in-memory engine, and flow-control config validation;
- template and compatibility tooling through `include_str!("../../etc/config-template.toml")`, TOML deserialization, `serde_ignored`, `reqwest::blocking::get`, and the persisted last config file.

The tests depend on external environment information through `SysQuota::memory_limit_in_bytes()` and CPU-count-derived defaults. They avoid brittle comparisons by normalizing those fields before asserting template/default equality.

## Risks and Edge Cases

- Several tests encode mutation during validation, not pure validation. Callers must expect `validate()` and `compatible_adjust()` to fill `Option` defaults, clamp compatibility flags, and rewrite RocksDB thresholds.
- Path-overlap rules differ depending on whether raft RocksDB or raft-engine is active. A future engine-mode change could accidentally reject valid raft-engine layouts or allow unsafe RocksDB raft/KV overlap.
- `test_config_template_matches_default` has a long manual normalization list. New computed defaults or template-only omissions must be added there, or the test can fail even when runtime behavior is valid.
- Percentage parsing is intentionally string-based. Accepting TOML floats later would change user-facing config syntax and invalidate the rejection guarantees in this chunk.
- Dynamic config tests assert manager side effects immediately after `update_config`; async or deferred manager implementations would need explicit synchronization or updated tests.
- `test_compatibility_with_old_config_template` depends on network access to GitHub and only treats timeout as non-fatal. Other transient network errors can fail the test.
- Flow-control validation rewrites user RocksDB settings only when thresholds are too large. Mistakes in the comparison direction can either disable flow-control protection or unexpectedly override stricter user settings.
- CDC and in-memory engine validation deliberately allow deprecated or zero values in some places for compatibility. Removing those allowances would be a breaking config change.

## Test and Validation Signals

This chunk itself is a dense set of unit/integration test signals. Useful follow-up validation for changes touching this area includes:

- run the config test module, especially tests named in this chunk: dynamic quota/server/storage/in-memory updates, config template validation, WAL path validation, region size inheritance, flow-control overrides, and CDC validation;
- verify `ConfigController::update_config` changes both the serialized current config and the live component managed by the registered module;
- deserialize commented `etc/config-template.toml` and assert no unrecognized keys are reported by `serde_ignored`;
- exercise both `EngineType::RaftKv` and `EngineType::RaftKv2` when changing computed defaults, because many expected values diverge by engine;
- validate with realistic cgroup/system memory limits because `memory_usage_limit`, block-cache percentage parsing, and background resource defaults use environment-derived values;
- inspect RocksDB CF options after validation and live flow-control toggles to confirm `level0_*`, pending-compaction byte limits, and `disable_write_stall` match the flow-control contract;
- persist a last config file and run `compatible_adjust(Some(last_cfg))` to confirm only intended compatibility fields are inherited.

## Chunk Handoff Notes

For final per-file reconciliation, merge this chunk as the test-tail companion to the production config definitions earlier in `sources/storage-engines/tikv/src/config/mod.rs`. It does not define new config structs, but it is the most explicit source for expected behavior around validation side effects, online-update propagation, template compatibility, path safety, and engine-dependent defaults.
