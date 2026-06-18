# subset-b-006922 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/AuthMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/AuthMonitor.cc

## Purpose
`AuthMonitor.cc` implements Ceph monitor authority for authentication state. It owns the Paxos-backed mutation path for CephX auth entries, rotating service keys, pending key promotion, global connection id allocation, bootstrap key creation, auth command handling, OSD key lifecycle helpers, auth handshake preprocessing, and auth map format upgrades.

## Important APIs, types, and functions
The main implementation is `AuthMonitor`, backed by `mon.key_server`, `pending_auth`, `max_global_id`, and `last_allocated_id`. Incremental mutation is funneled through `push_cephx_inc()`, `add_entity()`, `remove_entity()`, `process_used_pending_keys()`, and `increase_max_global_id()`. Paxos hooks are `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `encode_full()`, `get_trim_to()`, `preprocess_query()`, and `prepare_update()`.

Authentication flow is handled by `prep_auth()`, which selects an auth service handler, enforces CephX signature/version policy, assigns `peer_global_id`, drives `start_session()` or `handle_request()`, and triggers fast authentication completion. Command flow is split between read-only `preprocess_command()` for `auth export/get/list/print-key` and mutating `prepare_command()` for `auth add/import/get-or-create/fs authorize/caps/del/rotate/pending-key` operations. OSD provisioning calls use `validate_osd_new()`, `do_osd_new()`, `validate_osd_destroy()`, and `do_osd_destroy()`. Capability correctness is centralized in `valid_caps()`, `_check_and_encode_caps()`, `_merge_caps()`, and `_gen_wanted_caps()`. Upgrade helpers `_upgrade_format_to_dumpling()`, `_upgrade_format_to_luminous()`, and `_upgrade_format_to_mimic()` migrate stored cap/profile defaults.

## Control flow
On initial creation, the monitor clears secrets, seeds rotating keys, imports or creates bootstrap keyring entries, initializes `max_global_id`, and records auth format version 3. After each committed version, `update_from_paxos()` loads the latest full auth snapshot if available, then replays incremental records until `mon.key_server` reaches `get_last_committed()`. Version 1 cleanup removes the mkfs keyring once imported.

During normal operation, `tick()` and `on_active()` check whether the global-id allocation window is low, whether used pending keys need to be promoted, and whether rotating CephX keys need renewal. Leaders append incrementals and propose; peons send `MMonGlobalID` or `MMonUsedPendingKeys` requests to the leader and retry after proposals.

Auth handshakes enter through `preprocess_query()` or `prepare_update()`. Initial auth messages decode supported protocols and entity identity, filter CephX if required message features are absent, select cluster or service auth policy, allocate a global id, and run the selected service handler. If ids are exhausted, the request is waitlisted or forwarded to the leader until a new id range is committed.

Mutating commands validate JSON command maps, session presence, entity names, caps, supplied keyrings, and idempotency against both committed `key_server` state and uncommitted `pending_auth`. Successful mutations append CephX `AUTH_INC_ADD` or `AUTH_INC_DEL` incrementals and wait for the next commit before replying.

## State and persistence behavior
Auth state is Paxos persisted as versioned incrementals plus periodic full snapshots. Incrementals encode either `GLOBAL_ID` or CephX auth data; full snapshots encode `max_global_id` and the complete `KeyServer`. `encode_pending()` also recomputes `AUTH_BAD_CAPS` health checks by validating committed plus pending caps. Trimming keeps roughly twice `paxos_max_join_drift` versions on leaders.

`max_global_id` is committed cluster state, while `last_allocated_id`, `mon_num`, and `mon_rank` coordinate local id striping under `mon.auth_lock`. Pending key state lives inside `EntityAuth.pending_key` and is committed to `key` once clients report use after Quincy. Format upgrades are staged through normal pending incrementals, so upgrade effects are replicated like any other auth change.

## Dependencies and integration points
This file integrates with `PaxosService`, `MonitorDBStore`, `CephxKeyServer`, monitor sessions, `Messenger` connections, auth service handlers, `KeyRing`, MDS/OSD/MGR cap parsers, `ConfigMonitor` subscription refresh, OSD monitor provisioning workflows, MDS filesystem maps for `fs authorize`, and monitor feature/release gates. It sends and receives `MAuth`, `MAuthReply`, `MMonGlobalID`, `MMonUsedPendingKeys`, and `MMonCommand`.

## Risks and edge cases
Global-id exhaustion is sensitive because auth must sometimes become writable solely to allocate ids. `_assign_global_id()` depends on correct monitor rank/size setup and can return zero during rank changes. Pending-key code must avoid double-applying uncommitted entity updates; `auth get-or-create-pending` currently pushes the same incremental twice, which is worth test attention. `exists_and_matches_entity()` treats mismatched caps as errors for idempotent flows. Capability validation is configurable, so invalid non-mon caps may persist when full validation is disabled but later surface in health checks. Format upgrades use quorum feature gates and must remain rolling-upgrade safe.

## Test signals
Useful signals include mon bootstrap with and without mkfs keyring, auth command idempotency, malformed keyring import failure, cap parser errors and `AUTH_BAD_CAPS` health output, CephX signature/version rejection paths, global-id preallocation refill on leader and peon, OSD new/destroy key lifecycle, pending-key create/clear/commit/use promotion across Quincy gates, `fs authorize` cap merging, auth map full snapshot replay, and upgrade tests from format 0, 1, and 2 clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/AuthMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/AuthMonitor.h -->
# sources/distributed-fs/ceph/src/mon/AuthMonitor.h

## Purpose
`AuthMonitor.h` declares the monitor Paxos service that manages Ceph authentication metadata. It exposes the public auth-handshake, global-id, OSD key lifecycle, and diagnostic entry points while keeping command processing, auth map persistence, capability validation, and format upgrade machinery private.

## Important APIs, types, and functions
`AuthMonitor` derives from `PaxosService`. Its nested `Incremental` type is the persisted update record and has two variants: `GLOBAL_ID` for id range extension and `AUTH_DATA` for encoded `KeyServerData::Incremental` CephX changes. `auth_entity_t` groups `EntityName` with `EntityAuth` for OSD creation flows. The public methods include `_assign_global_id()`, `_set_mon_num_rank()`, `pre_auth()`, `tick()`, OSD create/destroy validation and apply methods, `dump_info()`, and `is_valid_cephx_key()`.

Private declarations cover bootstrap and upgrade helpers, keyring import/export, pending incremental encoding, Paxos hooks, command preprocess/prepare split, auth handshake preparation, cap validation and encoding, entity create/update/delete helpers, pending-key promotion, and global-id range management. The `caps_update` enum communicates whether `fs authorize` cap merging requires a stored update.

## Control flow
The header defines the service contract used by `Monitor`: read-only auth and auth handshakes can be handled during preprocess, while mutating auth commands and leader-only maintenance are prepared through Paxos. Bootstrap starts with `create_initial()`, normal updates replay through `update_from_paxos()`, and each new proposal starts from `create_pending()`.

## State and persistence behavior
Persistent state is represented by encoded `Incremental` records and full snapshots implemented in the `.cc` file. In-memory pending state is `std::vector<Incremental> pending_auth`; committed id allocation state is `max_global_id`; local id allocation cursor is `last_allocated_id`. `mon_num` and `mon_rank` are explicitly protected by `mon.auth_lock`, and the header documents that `_assign_global_id()` and `_set_mon_num_rank()` must be called under that lock.

## Dependencies and integration points
The declaration depends on Ceph auth primitives (`CephxKeyServer`, `KeyRing`, `EntityName`, `EntityAuth`), monitor persistence (`PaxosService`, `MonitorDBStore`), wire feature encoding, and monitor message request references. The `WRITE_CLASS_ENCODER_FEATURES(AuthMonitor::Incremental)` macro makes incrementals part of the Ceph encoding contract.

## Risks and edge cases
The header exposes `_assign_global_id()` publicly despite requiring lock discipline, so callers must honor the comment contract. `Incremental::decode()` asserts the enum range and assumes only known variants. Any new auth update kind requires changing both encoding and replay logic. `is_valid_cephx_key()` only validates base64 decoding into a `CryptoKey`; policy validation must happen elsewhere.

## Test signals
Compile-time encoder tests should cover all `Incremental::generate_test_instances()`. Runtime tests should verify lock-protected global id assignment, command routing through preprocess/prepare, OSD key helper contracts, pending-key feature gating, and backward-compatible decoding of auth incrementals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/AuthMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/mon/CMakeLists.txt

## Purpose
This CMake file defines the static `mon` library for Ceph monitor code. It collects monitor services, Paxos code, auth handlers, capability parsers, and monitor subsystems into one link target consumed by the monitor daemon build.

## Important APIs, types, and functions
The relevant build variables are `lib_mon_srcs`, `HAVE_GSSAPI`, `WITH_JAEGER`, and the `mon` static library target. `lib_mon_srcs` lists core monitor implementation files including `Paxos.cc`, `PaxosService.cc`, `Monitor.cc`, `AuthMonitor.cc`, `ConfigMonitor.cc`, `Elector.cc`, `ElectionLogic.cc`, `ConnectionTracker.cc`, and several monitor services.

## Control flow
There is no runtime control flow. At configure/build time, CMake expands `lib_mon_srcs`, conditionally appends object files or Kerberos auth sources, creates `add_library(mon STATIC ...)`, and links common dependencies into the target.

## State and persistence behavior
The file has no runtime state or persistence. Its state is the static source graph and conditional target links. Build configuration flags determine whether `mgr_cap_obj`, Kerberos auth service handling, and Jaeger base support are included.

## Dependencies and integration points
The target links `legacy-option-headers`, `kv`, `heap_profiler`, `${FMT_LIB}`, and optionally `jaeger_base`. It reaches outside `src/mon` for auth, MDS, MGR, and OSD capability code, reflecting that monitor command/auth handling depends on those cap parsers.

## Risks and edge cases
Build skew is the main risk: adding a monitor source or moving symbols requires keeping `lib_mon_srcs` synchronized. Optional sources guarded by `HAVE_GSSAPI`, `mgr_cap_obj`, or `WITH_JAEGER` must be available only when their targets/options exist. Since this target is static, missing source entries become link-time unresolved symbols in downstream binaries.

## Test signals
Build tests should cover default monitor builds, GSSAPI-enabled builds, Jaeger-enabled builds, and builds with or without `mgr_cap_obj`. A clean link of the monitor daemon is the primary validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CommandHandler.cc -->
# sources/distributed-fs/ceph/src/mon/CommandHandler.cc

## Purpose
`CommandHandler.cc` implements a small monitor command parsing helper. Its only behavior is canonical parsing of boolean command arguments accepted by monitor command handlers.

## Important APIs, types, and functions
`CommandHandler::parse_bool(std::string_view str, bool* result, std::ostream& ss)` accepts textual false values `false`, `no`, and numeric `0`, and true values `true`, `yes`, and numeric `1`. It uses `strict_strtoll()` to reject non-canonical numeric input and writes a human-readable error string on failure.

## Control flow
The function asserts `result` is non-null, tries to parse the string as base-10 integer, checks explicit false spellings or parsed zero, checks explicit true spellings or parsed one, and otherwise returns `-EINVAL` after writing the accepted value set into `ss`.

## State and persistence behavior
There is no retained state or persistence. The function mutates only `*result` and the supplied error stream.

## Dependencies and integration points
The file depends on `common/strtol.h` for strict numeric parsing and `ceph_assert` for contract enforcement. It is compiled into the `mon` library and can be inherited by monitor command handlers that need uniform boolean parsing.

## Risks and edge cases
The parser is deliberately case-sensitive and accepts only exact text. Numeric strings other than exactly valid `0` or `1` are rejected, including values like `2`. Passing a null result pointer aborts in debug/assert-enabled builds.

## Test signals
Unit coverage should verify all accepted spellings, invalid strings, invalid numbers, empty input, and non-null result enforcement. Command-level tests should confirm error text is surfaced to users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CommandHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CommandHandler.h -->
# sources/distributed-fs/ceph/src/mon/CommandHandler.h

## Purpose
`CommandHandler.h` declares a common base helper for monitor command handlers. It currently standardizes parsing of true/false-like command arguments.

## Important APIs, types, and functions
`class CommandHandler` exposes `int parse_bool(std::string_view str, bool* result, std::ostream& ss)`. The documented contract requires a non-null `result`, returns zero on success, returns `-EINVAL` on parse failure, and uses the stream for an explanatory error message.

## Control flow
The header contains no executable flow beyond the interface contract. Implementations include this header and call `parse_bool()` when converting command-map values into booleans.

## State and persistence behavior
The class has no fields and no persistence. It is a stateless utility object/base class.

## Dependencies and integration points
The header depends only on forward declarations via `<iosfwd>` and `std::string_view`. It can be included widely without pulling in monitor internals.

## Risks and edge cases
Because the helper is not static, users need an instance or base class relationship to call it. Adding more parsing helpers here would affect all monitor code that includes this common header, so dependencies should remain light.

## Test signals
Compile tests should verify inclusion from command handler implementations without extra dependencies. Functional signals come from `CommandHandler.cc` boolean parsing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CommandHandler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMap.cc -->
# sources/distributed-fs/ceph/src/mon/ConfigMap.cc

## Purpose
`ConfigMap.cc` implements in-memory normalization, precedence, masking, display, and change-log helpers for monitor-stored cluster configuration. It converts key/value records from the monitor KV namespace into sections and masked options, then resolves effective config for a daemon identity, CRUSH location, and device class.

## Important APIs, types, and functions
`MaskedOption::get_precision()` ranks CRUSH/device-class masks, while `OptionMask::dump()`, `MaskedOption::dump()`, `Section::dump()`, and `ConfigMap::dump()` provide formatter output. `Section::get_minimal_conf()` emits only minimal or no-monitor-update options that belong in generated config files.

`ConfigMap::generate_entity_map()` is the core resolver. It walks `global`, daemon type, name prefix components, and full entity sections; filters by device class and CRUSH location; applies mask precision within an option; and optionally records `ValueSource` metadata. `parse_mask()` parses command/config section selectors such as `global`, `osd`, `osd.3`, `rack:foo`, and `class:ssd`. `parse_key()` splits KV keys into option name and target selector, with special handling for `/mgr/` module option keys. `add_option()` resolves the `Option`, pre-validates its raw value, rejects invalid masks and `FLAG_NO_MON_UPDATE`, and inserts it into the right section. `ConfigChangeSet::dump()` and `print()` format history records.

## Control flow
Loading code calls `parse_key()` for each persisted key, then `add_option()` with an option lookup callback. Resolved maps are produced by first building an ordered list of applicable sections: global, type, each dotted name prefix, and full name. Each option is considered in insertion order, filtered by mask, and then either overrides prior values or is skipped when a previous masked option has greater precision. History formatting simply walks the stored key-to-old/new diff map.

## State and persistence behavior
`ConfigMap` itself is in-memory state. It stores `global`, `by_type`, `by_id`, and fabricated `stray_options` for unrecognized keys so unknown persisted options can still be represented. `ConfigChangeSet` models persisted history loaded by `ConfigMonitor`, but this file only formats it. No store I/O happens here.

## Dependencies and integration points
The implementation depends on Ceph `Option` metadata, `EntityName` parsing, `CrushWrapper` type ids and class/location data, `Formatter`, and monitor debug logging. `ConfigMonitor` owns loading from and writing to KV storage and delegates resolution to this map.

## Risks and edge cases
Mask precedence is subtle: CRUSH precision is only compared within a section, while section order still gives daemon type or entity-specific config priority over global masks. Unknown options are accepted as `LEVEL_UNKNOWN` unless later rejected by validation rules. `parse_key()` special-cases `/mgr/`, so module-option key shape changes can break name/who splitting. `add_option()` logs pre-validation failures but still inserts the normalized value path unless later checks reject it.

## Test signals
Good tests include global/type/id precedence, dotted client name prefix resolution, CRUSH mask precision, class masks, invalid target masks, unknown options, rejected no-mon-update options, `/mgr/` key parsing, generated minimal conf output, and formatted change-set output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMap.h -->
# sources/distributed-fs/ceph/src/mon/ConfigMap.h

## Purpose
`ConfigMap.h` defines the monitor configuration data model used after persisted config keys are loaded from KV storage. It captures option masks, masked option values, sections, whole-map resolution, and history diff records.

## Important APIs, types, and functions
`OptionMask` stores optional CRUSH `location_type/location_value` and `device_class`, with `empty()`, `to_str()`, and formatter dumping. `MaskedOption` stores a raw value, an `Option` pointer, mask, optional fabricated unknown option owner, and localized name. `Section` is a multimap from option name to masked options and can dump or emit minimal config.

`ConfigMap` owns `global`, `by_type`, `by_id`, and `stray_options`. Its APIs include `find_section()`, `clear()`, `dump()`, `generate_entity_map()`, `parse_key()`, `parse_mask()`, and `add_option()`. `ConfigChangeSet` records a committed config version, timestamp, description, and per-key old/new optional values.

## Control flow
The header describes the precedence order directly in comments: global, location masks, daemon type, device class, daemon-type location masks, and daemon name. Runtime code follows this model by loading sections and resolving effective values for a named entity.

## State and persistence behavior
All types are in-memory representations. The raw persisted key/value payload remains in `ConfigMonitor`; `ConfigMap` stores decoded strings and option metadata. `ConfigChangeSet` mirrors historical KV records so callers can print or dump previous config changes.

## Dependencies and integration points
The header depends on Ceph `Option`, `EntityName`, `version_t`, and `utime_t`, and forward-declares `CrushWrapper`. It is shared by `ConfigMonitor` and any code needing to resolve monitor-stored config for sessions or `MGetConfig` requests.

## Risks and edge cases
`MaskedOption` is move-only and deletes assignment operators, so container operations must construct/insert carefully. `ValueSource` stores raw pointers to `MaskedOption` entries; callers must not retain them after the map changes. `stray_options` owns fabricated options for unknown keys and must outlive `MaskedOption::opt` references.

## Test signals
Compile tests should cover move-only insertion into section multimaps. Runtime tests should cover pointer validity during resolution, unknown option ownership, mask string formatting, and `ConfigChangeSet` optional old/new combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMap.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMonitor.h -->
# sources/distributed-fs/ceph/src/mon/ConfigMonitor.h

## Purpose
`ConfigMonitor.h` declares the monitor Paxos service responsible for cluster configuration state. It exposes loading, command handling, config delivery, subscription checks, and Paxos lifecycle hooks.

## Important APIs, types, and functions
`ConfigMonitor` derives from `PaxosService`. Its state fields are `version`, `ConfigMap config_map`, `pending`, `pending_description`, `pending_cleanup`, and `current`. `pending` and `pending_cleanup` map string keys to optional bufferlists, where an empty optional means removal. Public APIs include `load_config()`, `load_changeset()`, command preprocess/prepare methods, `handle_get_config()`, Paxos hooks, `refresh_config()`, `maybe_send_config()`, `send_config()`, and subscription helpers.

## Control flow
The header establishes a two-lane flow: read-only commands and config fetches can be answered from the loaded `config_map`, while mutating commands are prepared, encoded to KVMonitor, and then committed through Paxos. Subscriptions are checked after version advances or when sessions request config updates.

## State and persistence behavior
The declaration shows that `ConfigMonitor` keeps in-memory current/pending maps, not the durable key/value store itself. Persistence is implemented by `encode_pending_to_kvmon()` and `encode_pending()` in the `.cc` file; `encode_full()` is intentionally empty because this service's real data is in KVMonitor.

## Dependencies and integration points
The header depends on `ConfigMap`, `PaxosService`, Ceph bufferlists, monitor sessions, and subscriptions. It is used by `Monitor` to route config commands, daemon config requests, auth completion subscription checks, and periodic service ticks.

## Risks and edge cases
Because the private `encode_pending_to_kvmon()` is separate from `encode_pending()`, callers preparing mutations must remember to enqueue KV changes before proposing ConfigMonitor state. Any future full-state behavior must account for the empty `encode_full()` override.

## Test signals
Compile coverage should confirm the service satisfies `PaxosService` overrides. Runtime tests should validate pending optional semantics, subscription update behavior, and empty full-encode behavior during monitor sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConnectionTracker.cc -->
# sources/distributed-fs/ceph/src/mon/ConnectionTracker.cc

## Purpose
`ConnectionTracker.cc` implements monitor-to-monitor connectivity scoring, peer report exchange, persistence-ready encoding, rank-change cleanup, and netsplit detection. Election code uses these scores to prefer better-connected leaders under the connectivity election strategy.

## Important APIs, types, and functions
`ConnectionTracker::receive_peer_report()` imports newer peer reports by epoch and version. `increase_epoch()` resets local version for a new election epoch, while `increase_version()` updates local report version and periodically asks the owner to persist scores. `report_live_connection()` and `report_dead_connection()` adjust exponentially aged per-peer scores and current liveness. `get_total_connection_score()` sums how peers view a candidate rank. `notify_rank_changed()` and `notify_rank_removed()` rewrite local and peer report rank-indexed maps after monmap changes.

`DirectedGraph` supports `get_netsplit()` by storing incoming/outgoing directed edges. Encoding and diagnostics are implemented by `encode()`, `decode()`, `get_encoded_bl()`, `dump()`, `ConnectionReport::dump()`, and test-instance generators.

## Control flow
Live/dead reports auto-initialize history scores to 1.0, then move scores toward one or zero by `units / (2 * half_life)`, clamp to `[0,1]`, set current liveness, and bump the version. Every `persist_interval` versions, the tracker calls `RankProvider::persist_connectivity_scores()`.

Peer reports are accepted only if their epoch is newer or their version is newer within the same epoch. Encoding is cached in `encoding` and cleared whenever state changes. Netsplit detection copies local reports into `peer_reports`, builds a directed graph of currently connected monitor pairs excluding known down monitors, then returns normalized monitor pairs with no observed bidirectional communication and at least incoming-edge presence.

## State and persistence behavior
The tracker stores `epoch`, `version`, `peer_reports`, `my_reports`, `half_life`, owner pointer, local `rank`, `persist_interval`, cached encoded buffer, and `CephContext`. `ConnectionReport` stores rank, current liveness map, historical score map, report epoch, and epoch version. Persistence is external: the tracker only encodes itself and asks its `RankProvider` owner to write it.

## Dependencies and integration points
The file depends on Ceph encoding, formatter, debug logging, `RankProvider`, and monitor election code. `Elector` owns a `ConnectionTracker`, persists it in the monitor store, sends encoded reports in election and ping messages, and queries netsplit pairs for health/reporting.

## Risks and edge cases
Negative or self ranks are dropped or logged, but rank-removal rewriting is complex and depends on ordered maps. `get_total_connection_score()` assumes `current` contains entries matching `history`; missing `current` entries would dereference an invalid iterator. Netsplit detection mutates `peer_reports[rank]` inside a query. Score aging uses caller-supplied time units and assumes they are bounded by real elapsed time. Persist interval zero would be unsafe, so configuration must avoid it.

## Test signals
Tests should cover live/dead score movement and clamping, peer report freshness rules, encode/decode round trips, cached encoding invalidation, persist callback frequency, rank change/removal map rewriting, clean tracker checks, netsplit detection with down monitors, and malformed/missing current/history pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConnectionTracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConnectionTracker.h -->
# sources/distributed-fs/ceph/src/mon/ConnectionTracker.h

## Purpose
`ConnectionTracker.h` declares the data structures and owner interface for monitor connectivity scoring. It provides the serialized report format exchanged between monitors and persisted locally for election decisions.

## Important APIs, types, and functions
`ConnectionReport` contains rank, current liveness, historical scores, epoch, and epoch version, plus Ceph encode/decode, equality, dumping, and test-instance generation. `DirectedGraph` stores incoming and outgoing edges for netsplit detection. `RankProvider` abstracts the owning monitor's rank and persistence callback.

`ConnectionTracker` exposes peer report ingestion, epoch/version updates, live/dead reports, half-life configuration, total score queries, cleanliness checks, netsplit detection, encode/decode, cached encoded buffer access, reset/rank notifications, formatter dumping, and test-instance generation.

## Control flow
The header documents the intended score update formula and owner callback behavior: score updates bump the version, and version multiples of the persist interval are persisted through `RankProvider`. Election code calls total-score queries only when the local rank is known.

## State and persistence behavior
`ConnectionTracker` owns all score state in memory and is serializable through `WRITE_CLASS_ENCODER(ConnectionTracker)`. The owner pointer is not serialized; decoded trackers are data snapshots used for import or persistence restore. `clear_peer_reports()` resets reports while preserving the current rank in `my_reports`.

## Dependencies and integration points
The header depends on Ceph encoding and basic monitor types. It is included by `ElectionLogic` and `Elector`; election messages carry encoded tracker data and the monitor store persists the encoded tracker under the elector's keys.

## Risks and edge cases
Decoded snapshots have no owner, so methods that trigger persistence should not be called on decoded peer snapshots. Copy construction preserves owner and context pointers, which is useful for stable election snapshots but requires care if copied across lifetimes. Rank-indexed maps must be updated when monmap ranks change or monitors are removed.

## Test signals
Encoder tests should use generated instances for `ConnectionReport` and `ConnectionTracker`. Integration tests should verify snapshots imported from messages do not persist, owner-backed trackers do persist, and rank reset/change/removal paths keep `is_clean()` true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConnectionTracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CreatingPGs.h -->
# sources/distributed-fs/ceph/src/mon/CreatingPGs.h

## Purpose
`CreatingPGs.h` defines the serialized monitor-side state for placement groups and pools that are in the process of being created. OSDMonitor uses this structure to remember in-flight PG creation progress across OSD map updates and monitor persistence.

## Important APIs, types, and functions
`creating_pgs_t` contains `last_scan_epoch`, a map of creating `pgs`, a pool creation `queue`, and `created_pools`. Nested `pg_create_info` stores creation epoch/time, up/acting sets, primaries, PG history, and past intervals. Nested `pool_create_info` stores pool creation epoch/time, current start index, target end, and `done()`.

Helpers include `still_creating_pool()`, `create_pool()`, `remove_pool()`, encode/decode/dump methods, and test-instance generators. Encoder macros expose feature-aware encoding for `pg_create_info` and `creating_pgs_t`.

## Control flow
Pool creation calls `create_pool()` to enqueue a range `[0, pg_num)` and mark the pool as created. As PGs are materialized, OSDMonitor updates `queue.start` and moves entries into `pgs`. `still_creating_pool()` checks both active PGs and queued work. `remove_pool()` erases all PGs in the target pool range plus queue and created-pool state.

## State and persistence behavior
The structure is pure persisted state. Encoding version 3 includes full `pg_create_info`; pre-Octopus feature encoding falls back to legacy pair-like create epoch/stamp data. Decoding handles older structures by reading a count and legacy PG records. `created_pools` prevents duplicate pool creation scheduling.

## Dependencies and integration points
The header depends on Ceph encoding, `utime_t`, and OSD types such as `pg_t`, `pg_history_t`, and `PastIntervals`. It is integrated with OSDMonitor's map update and PG creation logic, not standalone runtime code.

## Risks and edge cases
Backward compatibility is central: pre-Octopus instances lack up/acting/history fields, so users of decoded legacy records must tolerate defaults. `remove_pool()` relies on `pg_t` ordering by pool id and lower-bound ranges. `create_pool()` asserts the pool was not already marked created, so callers must check or maintain idempotency externally.

## Test signals
Encoder tests should cover current and legacy feature paths, empty and populated queues, pool removal range erasure, duplicate pool creation assertions, `done()` boundary behavior, and dump output including PG history and past intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CreatingPGs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ElectionLogic.cc -->
# sources/distributed-fs/ceph/src/mon/ElectionLogic.cc

## Purpose
`ElectionLogic.cc` implements the monitor election decision algorithm independent of monitor messaging and storage details. It tracks election epochs, votes, deferrals, victory validation, disallowed leaders, and connectivity-based leader preference, delegating side effects to `ElectionOwner`.

## Important APIs, types, and functions
Core lifecycle methods are `init()`, `bump_epoch()`, `start()`, `end_election_period()`, `declare_victory()`, `receive_propose()`, `receive_ack()`, and `receive_victory_claim()`. Strategy-specific proposal handlers are `propose_classic_handler()`, `propose_disallow_handler()`, and `propose_connectivity_handler()`. Helpers include `propose_classic_prefix()`, `defer()`, `connectivity_election_score()`, `victory_makes_sense()`, `clear_live_election_state()`, `reset_stable_tracker()`, and `connectivity_bump_epoch_in_election()`.

## Control flow
`start()` initializes or validates the persisted epoch, bumps to an odd election epoch if needed, marks itself as voting for itself, snapshots connectivity state for connectivity elections, sends proposals through the owner, and starts the owner's election timer. Proposals are ignored if self-originated, then routed by strategy. Classic elects lower rank; disallow extends classic by excluding configured ranks; connectivity ranks candidates by disallow status, aggregate connection score, and rank tie-breakers.

When an election timer ends, a node that has a majority of acknowledgements declares victory; otherwise it either starts another election if it has ever participated or asks the owner to reset/bootstrap. Victory bumps to the next even epoch and sends the acked quorum to the owner. Incoming acknowledgements add to `acked_me` only while `electing_me`; acknowledgements from a newer epoch cause a bump and restart. Incoming victory claims must make sense for the strategy and have the expected even epoch, otherwise connectivity mode can bump and restart.

## State and persistence behavior
`epoch` is the persisted election counter read and written through `ElectionOwner`. Odd epochs mean election in progress; even epochs mean stable. `last_election_winner`, `last_voted_for`, `leader_acked`, `electing_me`, `participating`, `acked_me`, `stable_peer_tracker`, and `leader_peer_tracker` are live election state. `bump_epoch()` persists the epoch, updates the peer tracker epoch, clears vote state, and notifies the owner.

## Dependencies and integration points
The logic depends on `ElectionOwner` for persistence, monitor rank/quorum metadata, proposal/ack/victory messaging, election reset, and feature-specific state. Connectivity strategy depends on `ConnectionTracker` score snapshots. `Elector` is the concrete owner in monitor runtime.

## Risks and edge cases
Election correctness depends on all monitors using the same strategy. Connectivity mode has the most subtle invariants: stable snapshots must avoid score changes mid-election, leader tracker comparisons must prevent incompatible deferrals, and out-of-quorum proposal suppression uses an ignore margin to reduce flapping. `receive_ack()` assumes ack epochs are odd. `receive_victory_claim()` records `last_voted_for = leader_acked`, which may be `-1` after unusual state transitions.

## Test signals
Tests should cover first boot epoch initialization, restart from odd persisted epochs, classic rank wins, disallowed leader exclusion, connectivity score tie-breaking, out-of-quorum proposal suppression, majority timeout victory, failed timeout reset, newer-epoch ack restart, invalid victory restart, and standalone victory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ElectionLogic.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ElectionLogic.h -->
# sources/distributed-fs/ceph/src/mon/ElectionLogic.h

## Purpose
`ElectionLogic.h` declares the side-effect-free monitor election state machine interface and its owner callback contract. It separates the algorithm from monitor-specific messaging, timers, storage, monmap, and quorum management.

## Important APIs, types, and functions
`ElectionOwner` is the callback interface for persisting epochs, validating local store writes, triggering elections, getting rank/quorum/disallowed leader data, sending proposals, resetting elections, deferring, announcing victory, and querying current quorum membership. `ElectionLogic` declares strategies `CLASSIC`, `DISALLOW`, and `CONNECTIVITY`, public state `participating`, `electing_me`, and `acked_me`, and public methods for standalone victory, election start/end, proposal/ack/victory reception, and epoch/winner reads.

Private helpers implement epoch initialization and bumping, proposal handlers, connectivity scoring, deferral, victory declaration, victory sanity checks, and live-state reset.

## Control flow
The header's comments define the election protocol: start enters an odd election epoch and proposes; proposal handlers may defer or trigger a new election; timer expiry either declares victory with majority acks or restarts/resets; victory claims end the election only when consistent with local strategy and epoch.

## State and persistence behavior
Only `epoch` is persisted, via `ElectionOwner`. The rest of the fields are in-memory election state and connectivity snapshots. The contract says `paxos_size()` and disallowed leader sets can change between elections but not during one.

## Dependencies and integration points
The header forward-declares `ConnectionTracker` and uses Ceph context, bufferlist, and epoch types. `Elector` implements `ElectionOwner` and wires this logic to monitor messages and store writes. The strategy enum must stay synchronized with `MonMap.h`.

## Risks and edge cases
The owner interface is large and correctness-critical; any owner implementation must preserve callback semantics such as durable epoch writes before messaging. Public `acked_me` and `electing_me` are exposed for `Elector` logging/metadata handling, so external code can observe live state but should not mutate protocol invariants. Strategy enum drift with `MonMap` would break mixed monitor behavior.

## Test signals
Interface tests can use a fake `ElectionOwner` to assert callback ordering, persisted epoch transitions, proposal payload behavior, and strategy-specific decisions without monitor networking. Build tests should catch enum/API drift with `Elector`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ElectionLogic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Elector.cc -->
# sources/distributed-fs/ceph/src/mon/Elector.cc

## Purpose
`Elector.cc` connects `ElectionLogic` to real monitor runtime. It persists election/connectivity state, sends and receives election messages, validates peer features/releases, manages election expiry timers, handles connectivity pings, assimilates connection reports, updates ping state across monmap rank changes, and calls monitor win/lose/bootstrap hooks.

## Important APIs, types, and functions
Constructor `Elector::Elector()` initializes `ElectionLogic`, `ConnectionTracker`, timeouts, and loads persisted connectivity scores. `ElectionOwner` methods implemented here include `persist_epoch()`, `read_persisted_epoch()`, `validate_store()`, `notify_bump_epoch()`, `trigger_new_election()`, `propose_to_peers()`, `_start()`, `_defer_to()`, `message_victory()`, and membership/rank helpers. Connectivity persistence uses `persist_connectivity_scores()`.

Message handlers are `dispatch()`, `handle_propose()`, `handle_ack()`, `handle_victory()`, `nak_old_peer()`, `handle_nak()`, and `handle_ping()`. Timer and ping machinery lives in `reset_timer()`, `cancel_timer()`, `begin_peer_ping()`, `send_peer_ping()`, `ping_check()`, `begin_dead_ping()`, `dead_ping()`, and `process_pending_pings()`. Monmap updates use `notify_clear_peer_state()`, `notify_rank_changed()`, `notify_rank_removed()`, and `notify_strategy_maybe_changed()`.

## Control flow
Election start clears peer info, records local features/release/metadata, and arms a timeout. Proposals are broadcast to all other monitors with encoded connection scores, local monmap, strategy, and supported features. Deferral sends an `OP_ACK` to the chosen leader and extends the timer. Victory computes intersection of cluster and monitor features across acked peers, selects minimum monitor release, sends `OP_VICTORY` plus leader command payload to quorum members, and calls `Monitor::win_election()`.

`dispatch()` validates message type, participation, sender rank, fsid, sender monmap membership, monmap epoch freshness, strategy consistency, and optional scoring data. If a peer has a newer monmap, the elector persists it locally, cancels election, notifies the monitor, and bootstraps. Propose messages are handled before old-epoch dropping so old out-of-quorum proposals can trigger elections. Ack/victory/nak messages with old epochs are dropped.

Ping flow starts only when quorum features support monitor pinging. Live pinging sends `MMonPing`, schedules periodic checks, marks missed acknowledgements dead, and degrades scores. Dead pinging continues degrading until a ping reply or later begin-peer-ping moves the peer back live. Ping messages always carry tracker data, so monitors exchange connectivity state opportunistically.

## State and persistence behavior
`persist_epoch()` writes `election_epoch` and `connectivity_scores` to `MonitorDBStore`; score-only persistence writes just `connectivity_scores`. Runtime state includes the expire timer, peer feature metadata for victory, pending pings before quorum features are known, sent/acked ping timestamps, live/dead ping sets, timeout settings, disallowed leader set, and the owned connection tracker.

## Dependencies and integration points
This file depends on `Monitor`, `MonitorDBStore`, `Timer`, `Messenger`, `MonMap`, `MMonElection`, `MMonPing`, Ceph feature sets, and `ElectionLogic`/`ConnectionTracker`. It calls monitor methods for election lifecycle (`join_election`, `start_election`, `bootstrap`, `win_election`, `lose_election`, `notify_new_monmap`) and command sharing.

## Risks and edge cases
Feature/release mismatches can trigger NAK and process exit for an outdated monitor. Monmap replacement during election must be durable before bootstrap. Pinging is gated by quorum features; pending pings must be drained after quorum forms. Rank removal rewrites ping sets manually and can leave scheduled callbacks racing with changed ranks. `handle_ping()` maps source address to rank and drops unknown removed monitors. Connectivity data from messages must match strategy expectations, especially in mixed or transitioning clusters.

## Test signals
Tests should cover proposal/ack/victory message handling, feature and release NAKs, newer/older monmap paths, timer expiry callbacks, win/lose monitor calls, leader command sharing, ping live/dead transitions, pending pings before quorum feature establishment, rank change/removal cleanup, persisted epoch/connectivity store keys, strategy mismatch dropping, and unknown ping source drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Elector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Elector.h -->
# sources/distributed-fs/ceph/src/mon/Elector.h

## Purpose
`Elector.h` declares the monitor election integration class. `Elector` owns the election algorithm and connectivity tracker, implements both `ElectionOwner` and `RankProvider`, and exposes monitor-facing hooks for dispatching election/ping messages and reacting to monmap or strategy changes.

## Important APIs, types, and functions
`Elector` contains `ElectionLogic logic`, `ConnectionTracker peer_tracker`, ping timestamp maps, live/dead/pending ping sets, timer state, peer feature metadata, monitor pointer, and disallowed leader set. Internal message handlers cover propose, ack, victory, NAK, ping, and connection report assimilation. Owner-interface methods expose epoch persistence, store validation, election triggers, peer proposals, deferral, victory messaging, quorum membership, stretch-mode checks, and connectivity score persistence.

Public monitor APIs include constructor/destructor, `shutdown()`, `get_epoch()`, `declare_standalone_victory()`, `begin_peer_ping()`, `dispatch()`, `call_election()`, `stop_participating()`, `start_participating()`, peer tracker inspection, netsplit query, peer-state reset/rank notifications, strategy update, disallowed leader update, pending ping processing, and connection score dumping.

## Control flow
The header defines a layered flow: external monitor code calls `call_election()` or `dispatch()`, private handlers validate and translate messages, `ElectionLogic` makes the decision, and owner callbacks send messages or update monitor state. Connectivity pings run as self-rescheduling timer callbacks and feed the tracker used by connectivity elections.

## State and persistence behavior
Persistent state is not written in the header, but the declared owner methods persist election epochs and connectivity scores in the implementation. Runtime state includes timer callback `expire_event`, peer feature metadata collected during self-election, ping maps/sets, disallowed leaders, and pending pings waiting for quorum feature negotiation.

## Dependencies and integration points
The class depends on `Monitor`, `MonOpRequest`, `mon_types`, `ElectionLogic`, `ConnectionTracker`, and `Formatter`. It is the bridge between monitor networking/timers/store and the pure election decision engine.

## Risks and edge cases
`Elector` inherits `RankProvider` privately via `class Elector : public ElectionOwner, RankProvider`; only internal conversion to the tracker is intended. The public `Elector *elector` self-pointer is unusual and may exist for legacy call sites. `set_disallowed_leaders()` only records changes; callers must trigger elections if the current leader becomes disallowed. `start_participating()` only flips the flag in the declaration's implementation and does not itself call an election despite the comment.

## Test signals
Compile tests should ensure `Elector` still satisfies both owner interfaces after interface changes. Runtime tests should validate monitor lifecycle hooks, disallowed leader change behavior, start/stop participation semantics, pending ping draining, and exposed dump/netsplit methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Elector.h -->
