# sources/distributed-fs/ceph/src/mon/MgrMap.cc

## Purpose

`MgrMap.cc` implements the serializable monitor-side description of the Ceph manager cluster: the active mgr identity, active address vector, standby mgrs, enabled and always-on modules, module option metadata, exposed services, active clients to blocklist on failover, feature bits, and epoch/version summary output. It is the data object that `MgrMonitor` persists through Paxos and sends to clients and mgr daemons as `MMgrMap`.

## Important APIs, Types, and Functions

The main implementations are `MgrMap::ModuleOption`, `MgrMap::ModuleInfo`, `MgrMap::StandbyInfo`, and `MgrMap` encoding, dumping, and lookup helpers. `ModuleOption::encode/decode/dump()` preserves mgr-module option schema data such as type, level, flags, defaults, bounds, enum values, tags, and see-also links. `ModuleInfo::encode/decode/dump()` carries a module name, `can_run`, an error string, and its option table. `StandbyInfo::encode/decode/dump()` carries standby gid, daemon name, available modules, and mgr feature bits. Core helpers include `get_all_names()`, `get_always_on_modules()`, `all_support_module()`, `have_module()`, `get_module_info()`, `can_run_module()`, `create_null_mgrmap()`, `dump()`, and `print_summary()`.

## Control Flow and State

Encoding is compatibility-sensitive. Pre-Nautilus peers receive struct version 5 with legacy single active address encoding and old module-name sets; modern peers receive struct version 14 with address vectors, active-change time, always-on modules, active mgr features, failure OSD epoch, client name/address vectors, flags, and force-disabled modules. Decode handles historical struct versions by reconstructing `ModuleInfo` objects from old string sets, defaulting missing `active_change`, and validating that encoded client names and address vectors have matching sizes. `get_always_on_modules()` selects the current Ceph release's module set or the most recent earlier release set.

Persistent state is the encoded map stored by `MgrMonitor`. Runtime-only policy lives elsewhere, but the map carries failover-significant state: `active_gid`, `active_name`, `available`, `active_addrs`, `active_mgr_features`, `standbys`, `clients`, `services`, `last_failure_osd_epoch`, `FLAG_DOWN`, and `force_disabled_modules`.

## Dependencies and Integration Points

The file depends on Ceph buffer encoding macros, `entity_addrvec_t`, `utime_t`, `Option`, release helpers, JSON/formatter support, and feature negotiation (`SERVER_NAUTILUS`). It integrates with `MgrMonitor` for Paxos persistence and command output, with clients through `MMgrMap`, with `ConfigMonitor` through module options built from `available_modules`, and with OSD blocklisting through active mgr client addresses.

## Risks and Test Signals

Compatibility is the largest risk: field order, struct versions, and feature-gated address encoding must remain stable. A mismatch between client names and client address vectors throws malformed input. `can_run_module()` throws for unknown modules, so callers must check existence or intentionally surface that failure. Release fallback in `get_always_on_modules()` can silently return an older set. Useful tests are encode/decode round trips across legacy and modern feature masks, malformed client vector decode, JSON dump coverage, module option round trips, and command-level `mgr dump/module ls` output after map updates.
