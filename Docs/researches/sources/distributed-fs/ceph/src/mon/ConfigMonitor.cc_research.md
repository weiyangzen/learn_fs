<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/ConfigMonitor.cc

## Purpose
`ConfigMonitor.cc` implements the monitor service for cluster configuration commands, subscriptions, config delivery, config history, and cleanup of obsolete stored config keys. It stores actual config values through `KVMonitor` but uses its own PaxosService version to coordinate config-map refresh and client notification.

## Important APIs, types, and functions
`ConfigMonitor` maintains `version`, `config_map`, `pending`, `pending_cleanup`, `pending_description`, and `current`. Paxos hooks are `init()`, `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `get_trim_to()`, `tick()`, and `on_active()`. `encode_pending_to_kvmon()` writes pending set/removal operations and history records into `KVMonitor`.

Command paths are `preprocess_command()` for read-only commands (`config help`, `ls`, `dump`, `get`, `log`, `generate-minimal-conf`) and `prepare_command()` for mutating commands (`config set`, `rm`, `reset`, `assimilate-conf`). Config delivery uses `handle_get_config()`, `refresh_config()`, `maybe_send_config()`, `send_config()`, `check_sub()`, and `check_all_subs()`. Persistence readers are `load_config()` and `load_changeset()`.

## Control flow
On committed version advance, `update_from_paxos()` sets `version`, reloads config from KV storage, and checks all config subscriptions. Mutating commands first ensure `KVMonitor` is writable, parse and validate input, build `pending` key updates, remove no-op changes against `current`, enqueue changes/history into KVMonitor, plug Paxos, propose KVMonitor pending state, unplug Paxos, force ConfigMonitor proposal, and wait for the next commit.

`config set` validates options and values unless forced, rejects no-monitor-update options, parses target masks, and stores `section/mask/name` keys. `config rm` writes a removal. `config reset` walks history backward to reconstruct old values or removals. `config assimilate-conf` parses a supplied config file, imports valid monitor-updatable options not already conflicting with the store, and returns the leftover config text.

Read-only command flow uses `ConfigMap` to dump stored values or resolve values for a specific entity. OSD entities add CRUSH full location and device class before resolving. `handle_get_config()` answers daemon config fetch messages, while subscription checks resend only when `refresh_config()` changes a session's last config map.

## State and persistence behavior
Actual config keys live in monitor KV under `config/`. History lives under `config-history/<version>/`, with metadata at the prefix key, old values under `-key`, and new values under `+key`. ConfigMonitor's Paxos state stores only `last_committed` for its version. It keeps five old ConfigMonitor versions via `get_trim_to()`. `pending_cleanup` queues repairs for invalid or renamed persisted keys and is proposed on `tick()` when KVMonitor is writable.

`load_config()` rebuilds all in-memory state from KV, handles Pacific blacklist-to-blocklist renames, schedules cleanup when the cluster release allows it, and refreshes the local monitor's own runtime config with `g_conf().set_mon_vals()`.

## Dependencies and integration points
This file integrates `PaxosService`, `KVMonitor`, `MgrMonitor` module options, `OSDMonitor`/CRUSH location data, monitor sessions/subscriptions, `MConfig`, `MGetConfig`, `MMonCommand`, `ConfFile`, `Formatter`, and `TextTable`. It also relies on global Ceph option metadata and monitor map addresses for minimal config generation.

## Risks and edge cases
The service deliberately splits versioning from storage through KVMonitor, so proposals must keep ConfigMonitor and KVMonitor commits coordinated. The `config get` dump path iterates `config` and `src` maps in parallel even though they are different container types; source mapping correctness depends on matching insertion for each resolved value. History reset relies on complete history rows for recent versions only. `assimilate-conf` skips invalid/conflicting entries into returned text, so callers must inspect output. Renamed-key cleanup is gated by `min_mon_release`; mixed-release clusters need coverage.

## Test signals
High-value tests include set/rm/reset history behavior, forced and non-forced validation, no-op mutation suppression, KVMonitor writeability wait/retry, config log formatting, assimilate-conf leftovers, per-entity CRUSH/class resolution, subscription one-shot removal, local `g_conf` refresh, Pacific rename cleanup, and minimal config generation for legacy and modern monitor addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMonitor.cc -->
