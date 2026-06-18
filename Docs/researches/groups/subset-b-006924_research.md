# subset-b-006924 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrMap.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrMap.h -->
# sources/distributed-fs/ceph/src/mon/MgrMap.h

## Purpose

`MgrMap.h` declares the manager map model shared by monitors, manager daemons, and clients. It defines the exact state carried in a mgr map epoch and the public helpers for module support checks, active/standby identity queries, encoding, dumping, and summary rendering.

## Important APIs, Types, and Functions

`MgrMap::ModuleOption` models an option exported by a mgr module using Ceph `Option`-compatible type, level, flags, defaults, min/max, enum choices, descriptions, tags, and see-also fields. `MgrMap::ModuleInfo` describes an available module and whether it can run. `MgrMap::StandbyInfo` describes a standby daemon by gid, name, module list, and feature bits. The `MgrMap` object stores epochs, failure OSD epoch, `FLAG_DOWN`, active gid/addrs/name/availability/change time/features, active mgr RADOS clients, standbys, enabled modules, always-on modules by release, force-disabled always-on modules, available modules, and service URIs.

Key methods expose `get_epoch()`, `get_active_*()`, `get_num_standby()`, `all_support_module()`, `have_module()`, `get_module_info()`, `can_run_module()`, `module_enabled()`, `any_supports_module()`, `have_name()`, `get_all_names()`, `get_always_on_modules()`, `encode()`, `decode()`, `dump()`, and `print_summary()`.

## Control Flow and State

The header is mostly data structure and API contract. Inline helpers search active and standby state, distinguish enabled modules from always-on modules, and avoid exposing mutable state except through monitor-owned update paths. `create_null_mgrmap()` is a protocol helper used to force a mgr daemon that incorrectly believes it is active to reset its view.

## Dependencies and Integration Points

Dependencies include Ceph message address types, encoding macros, `Option`, `utime_t`, release constants, and formatter support. `WRITE_CLASS_ENCODER_FEATURES(MgrMap)` and nested encoder declarations make these types first-class Ceph wire/store payloads. `MgrMonitor`, `MMgrBeacon`, `MMgrMap`, CLI command handling, config option discovery, and failover/blocklist logic all depend on this schema.

## Risks and Test Signals

This header is a persistence and wire contract. Adding fields requires versioned encoding in `MgrMap.cc`, and changing inline semantics can affect CLI, module enablement, and failover. Tests should compile all encoder declarations, round-trip generated instances, verify active/standby name lookup, verify always-on plus force-disabled semantics, and exercise module support checks when active and standby module sets differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/MgrMonitor.cc

## Purpose

`MgrMonitor.cc` implements the monitor Paxos service that owns `MgrMap`. It elects and fails over active manager daemons from beacons, persists manager metadata and command descriptions, serves mgr-map subscriptions and CLI queries, updates health when no active mgr exists, manages always-on module policy, and blocklists old active mgr instances and their RADOS clients during failover.

## Important APIs, Types, and Functions

Important functions include `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `preprocess_query()`, `prepare_update()`, `preprocess_beacon()`, `prepare_beacon()`, `tick()`, `promote_standby()`, `drop_active()`, `drop_standby()`, `preprocess_command()`, `prepare_command()`, metadata helpers, subscription helpers, and digest helpers. The static `always_on_modules()` table defines release-keyed built-in mgr modules. `find_module_option()` normalizes `mgr/$module/$instance/$option` names to global module options for `ConfigMonitor`.

## Control Flow and State

Beacons are accepted only from sessions with `mgr` execute caps and matching fsid. `prepare_beacon()` handles daemon restarts, standby registration, active selection, active service/address/availability/module/client updates, command description capture on first available active beacon, and stale active self-reset through a null mgr map. `tick()` runs only on the leader and drops laggy standbys, drops laggy active daemons when OSDMonitor is writable, promotes standbys unless `FLAG_DOWN` is set, triggers delayed health warnings, and removes obsolete `orchestrator_cli`.

Paxos state is `pending_map` encoded as the next mgr map epoch plus metadata updates under `mgr_metadata`, health checks, and active mgr command descriptions under `mgr_command_descs`. Dropping the active plugs Paxos, blocklists active addresses and mgr-owned RADOS clients through `OSDMonitor`, records `last_failure_osd_epoch`, clears active state, forces an immediate proposal, and cancels digest timers.

CLI preprocessing serves read-only commands: `mgr stat`, `mgr dump`, `mgr module ls`, `mgr services`, `mgr metadata`, `mgr versions`, and `mgr count-metadata`. Update preparation implements `mgr set down`, `mgr fail`, `mgr module enable`, `mgr module disable`, and `mgr module force disable`, with wait-for-commit replies on successful proposals.

## Dependencies and Integration Points

This service integrates with `PaxosService`, `CommandHandler`, `OSDMonitor`, `ConfigMonitor`, `HealthMonitor`, monitor sessions and subscriptions, `MMgrBeacon`, `MMgrMap`, `MMgrDigest`, `MMonCommand`, mgr static commands, and the monitor store. Manager module option data is converted into `Option` objects and forces config reload. Digest subscribers receive health JSON and monitor status JSON periodically.

## Risks and Test Signals

Risks include failover races around daemon restart and old active blocklisting, incorrect Paxos plug/unplug ordering, stale command descriptions after active change, map updates while OSDMonitor is not writable, and module enablement decisions during rolling upgrades. `mgr module force disable` intentionally permits disabling always-on modules only after explicit confirmation. Tests should cover beacon promotion, active restart, standby restart, laggy active failover, `mgr set down`, blocklist epoch recording, metadata persistence/removal, command description persistence, module command errors, subscription delivery, digest timer cancellation, and health warning grace periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrMonitor.h -->
# sources/distributed-fs/ceph/src/mon/MgrMonitor.h

## Purpose

`MgrMonitor.h` declares the monitor service responsible for manager-map authority. It combines `PaxosService` persistence with `CommandHandler` command routing and exposes query/update hooks used by the monitor dispatcher.

## Important APIs, Types, and Functions

The class owns live `map`, `pending_map`, `ever_had_active_mgr`, pending metadata put/remove sets, module option cache, digest timer state, previous health checks, learned command descriptions, and beacon timeout tracking. Public service methods include initialization/shutdown, Paxos lifecycle (`create_initial`, `update_from_paxos`, `create_pending`, `encode_pending`, `get_trim_to`), query/update dispatch, beacon preprocessing/preparation, subscription handling, digest sending, active/restart hooks, ticking, summaries, metadata dumping/counting, version grouping, and `get_command_descs()`.

## Control Flow and State

Private helpers form the failover control surface: `promote_standby()`, `drop_active()`, and `drop_standby()`. `check_caps()` centralizes mgr beacon capability and fsid validation. `should_warn_about_mgr_down()` gates health severity based on OSD presence and grace periods. `last_tick` and `last_beacon` prevent false failovers after slow monitor election or delayed local ticks.

## Dependencies and Integration Points

The header ties together `MgrMap`, `PaxosService`, `MonCommand`, `CommandHandler`, `Context`, monitor subscriptions, and Ceph health maps. It is consumed by `Monitor`, `MgrStatMonitor` for active gid checks, config handling for module options, and command help paths that need manager-provided command descriptions.

## Risks and Test Signals

The main risk is that state declared here has mixed lifetimes: Paxos-persisted map fields, pending transaction fields, leader-local beacon timers, and transient digest state. Tests should distinguish restart behavior from persisted map behavior, verify pending metadata sets are cleared only after encoding, and ensure `last_beacon` reset behavior prevents false lag detection after elections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrStatMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/MgrStatMonitor.cc

## Purpose

`MgrStatMonitor.cc` implements the monitor Paxos service that persists manager-reported cluster statistics: `PGMapDigest`, service map, progress events, health checks, and pool availability tracking. It also serves statfs and pool-stat client requests from the latest committed digest.

## Important APIs, Types, and Functions

Key functions are the constructor/destructor config observer registration, `get_tracked_keys()`, `handle_conf_change()`, `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `preprocess_report()`, `prepare_report()`, `preprocess_getpoolstats()`, `preprocess_statfs()`, `check_subs()`, `send_digests()`, `calc_pool_availability()`, `clear_pool_availability()`, `should_calc_pool_availability()`, and `update_logger()`.

## Control Flow and State

Only reports from the current active mgr gid are accepted; non-active mgr reports are ignored in preprocessing. `prepare_report()` decodes a pending PG digest from `MMonMgrReport`, swaps in report health checks, service map data, and progress events, then the Paxos commit path encodes digest, service map, progress events, pool availability, and health checks. `update_from_paxos()` decodes optional fields defensively, notifies subscribers, updates cluster log counters, notifies OSDMonitor about new PG digest data, and leader-side calculates pool availability when the configured interval has elapsed.

Pool availability state is guarded by `lock`. The calculation adds pools from `digest.pool_pg_unavailable_map`, removes pools missing from the digest or OSDMap, updates uptime/downtime/failure counters based on availability transitions, and copies live availability into `pending_pool_availability`.

## Dependencies and Integration Points

The service depends on `PaxosService`, `PGMapDigest`, `ServiceMap`, progress events, health check maps, `OSDMonitor`, `MgrMonitor`, `MMonMgrReport`, `MGetPoolStats`, `MStatfs`, `MServiceMap`, config observation, and cluster logger counters. Service-map subscriptions use the `"servicemap"` subscription type.

## Risks and Test Signals

Risks include accepting stale/non-active mgr reports, decoding older Paxos records missing progress or availability fields, racing config changes with availability updates, and incorrect uptime/downtime transitions. Tests should verify active gid filtering, statfs and pool-stats capability checks, fsid mismatch drops, removed-pool statfs drops, service-map subscriptions, optional decode compatibility, config toggle reset behavior, and cluster logger counter updates from digest state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrStatMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrStatMonitor.h -->
# sources/distributed-fs/ceph/src/mon/MgrStatMonitor.h

## Purpose

`MgrStatMonitor.h` declares the monitor service that stores and serves mgr-reported PG, service, progress, health, and pool availability statistics. It also exposes lightweight accessors used by monitor status, statfs, and dump paths.

## Important APIs, Types, and Functions

Live state includes `version`, `PGMapDigest digest`, `ServiceMap service_map`, progress events, and pool availability. Pending Paxos state mirrors those fields as `pending_digest`, `pending_health_checks`, `pending_progress_events`, `pending_service_map_bl`, and `pending_pool_availability`. Public APIs include report preprocessing/preparation, statfs and poolstats preprocessing, subscription checks, digest sending, logger updating, pool availability calculation/clear/update gating, digest/statfs/pool-stat accessors, and config observer methods.

## Control Flow and State

The class is both a `PaxosService` and an `md_config_obs_t`. The mutex protects availability tracking and config-derived fields. `enable_availability_tracking`, `pool_availability_update_interval`, and `pool_availability_last_updated` determine whether availability scores are updated from the current digest. `get_trim_to()` keeps only a small history because old mgrstat states are not normally needed.

## Dependencies and Integration Points

Dependencies include `ceph_mutex`, `Context`, `PaxosService`, `PGMap`, `ServiceMap`, monitor subscriptions, config proxy callbacks, and statfs structures. Consumers use `get_service_map()`, `get_progress_events()`, `get_pool_stat()`, `get_digest()`, `get_pool_availability()`, `get_statfs()`, `dump_info()`, `dump_cluster_stats()`, and `dump_pool_stats()`.

## Risks and Test Signals

The header exposes references to live maps, so callers must respect monitor threading assumptions. Availability defaults are read from global config at construction and then updated by observer callbacks. Tests should cover construction/destruction observer registration, pending/live state separation, accessors on missing pools, availability config changes, and formatting helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MgrStatMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonCap.cc -->
# sources/distributed-fs/ceph/src/mon/MonCap.cc

## Purpose

`MonCap.cc` implements parsing, formatting, encoding, merging, and enforcement for monitor capabilities. Monitor caps authorize service-level read/write/execute access, named command grants with argument constraints, profiles that expand into grants, fs-name restrictions, and network restrictions.

## Important APIs, Types, and Functions

The file implements stream output for `mon_rwxa_t`, `StringConstraint`, `MonCapGrant`, and `MonCap`; `MonCapGrant::parse_network()`, `expand_profile()`, `get_allowed()`, and `to_string()`; and `MonCap::is_allow_all()`, `set_allow_all()`, `is_capable()`, `encode()`, `decode()`, `dump()`, `generate_test_instances()`, `parse()`, `merge()`, and `to_string()`. The Boost Spirit `MonCapParser` grammar accepts blanket grants, service grants, profile grants, command grants with `with` argument constraints, optional network clauses, and fs-name clauses.

## Control Flow and State

Parsing fills a vector of `MonCapGrant` objects and clears all grants on parse failure. Each grant can hold service/profile/command/fs/network fields plus rwx bits and command argument constraints. `expand_profile()` lazily populates cached profile grants for profiles such as `read-only`, `read-write`, `mon`, `osd`, `mds`, `mgr`, bootstrap profiles, RBD profiles, crash, cephfs-mirror, and role-definer. `is_capable()` iterates grants, skips invalid or non-matching networks, short-circuits `allow *`, ORs allowed bits from matching grants, and succeeds when all operation-required read/write/exec bits are present.

Encoded state is only the original textual cap string, preserving compatibility and re-parsing on decode. `merge()` updates or appends single fs-name grants idempotently.

## Dependencies and Integration Points

Dependencies include Boost Spirit/Fusion/Phoenix, regex, network parsing/matching helpers, Ceph auth entity names, buffer encoding, formatter support, and debug logging. Monitor sessions call `is_capable()` through `MonSession` to authorize monitor services and commands, including command argument constraints for bootstrap and blocklist operations.

## Risks and Test Signals

Risks include grammar ambiguity, profile grants becoming stale as command names change, regex exceptions, invalid network clauses silently denying a grant, and text-only persistence accepting old syntax but losing structured validation until decode. `MonCapGrant::to_string()` uses `else if` for rwx bits and therefore is only suitable for simple fs-name grant rendering, not full service/profile/command caps. Tests should cover valid and invalid parse cases, quoting, network filters, exact/prefix/regex argument constraints, profile expansion, `config-key` blanket denial except `allow *`, fs-name merge idempotency, encode/decode reparsing, and negative authorization cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonCap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonCap.h -->
# sources/distributed-fs/ceph/src/mon/MonCap.h

## Purpose

`MonCap.h` declares the monitor capability model used by Ceph auth to decide whether an entity may perform monitor service or command operations. It defines rwx bit constants, command argument constraints, grant structure, and the top-level `MonCap` container.

## Important APIs, Types, and Functions

`MON_CAP_R`, `MON_CAP_W`, `MON_CAP_X`, `MON_CAP_ALL`, and `MON_CAP_ANY` define monitor permission bits. `mon_rwxa_t` wraps the byte bitmask. `StringConstraint` supports none/equal/prefix/regex matching for command arguments. `MonCapGrant` stores service, profile, command, constrained command args, fs name, network string and parsed network, allow bits, and cached profile grants. `MonCap` stores original text plus grant vector and exposes parsing, merging, encoding, dumping, full capability checks, allow-all checks, allowed fs-name extraction, and `fs_name_capable()`.

## Control Flow and State

The header documents the five grant forms: blanket allow, service allow, profile, command with optional argument constraints, and fs-name restriction. `fs_name_capable()` handles direct fs-name grants, allow-all, and profile-expanded fs/mds grants for a requested mask. `allowed_fs_names()` returns a constrained list only when every grant is fs-name-specific; otherwise it returns an empty vector to signal unrestricted or mixed semantics.

## Dependencies and Integration Points

Dependencies include Ceph common forward declarations, entity names, address types, encoding macros, and buffer/formatter declarations. `WRITE_CLASS_ENCODER(MonCap)` makes the text capability persistable in auth records. Monitor command handling, session service checks, filesystem map filtering, and bootstrap key creation depend on these declarations.

## Risks and Test Signals

Any change to grants or matching semantics is security-sensitive. Tests should verify rwx masks, allow-all behavior, fs-name restriction behavior, mixed grant `allowed_fs_names()`, profile expansion through `fs_name_capable()`, network parsing fields, and encoding round trips through the text form.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonCap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonClient.cc -->
# sources/distributed-fs/ceph/src/mon/MonClient.cc

## Purpose

`MonClient.cc` implements the client-side monitor connection manager. It builds and refreshes monmaps, hunts for a monitor session, authenticates, renews subscriptions and auth tickets, sends monitor commands and tell commands, handles config pushes, sends log messages, serves authorizer requests for peer services, and exposes an admin socket key-rotation hook.

## Important APIs, Types, and Functions

Major functions include `build_initial_monmap()`, `get_monmap()`, `get_monmap_and_config()`, `ping_monitor()`, `ms_dispatch()`, `handle_monmap()`, `handle_config()`, `init()`, `shutdown()`, `authenticate()`, `_reopen_session()`, `_add_conns()`, `_finish_hunting()`, `tick()`, `_renew_subs()`, `_check_auth_tickets()`, `_check_auth_rotating()`, `wait_auth_rotating()`, `_send_command()`, `_check_tell_commands()`, `_resend_mon_commands()`, command reply handlers, version reply handling, AuthClient/AuthServer callbacks, and all `MonConnection` auth helpers. The custom `monc_category()` maps local async errors to standard conditions and negative errno values.

## Control Flow and State

The session state machine is protected by `monc_lock`. When no session is open, `_reopen_session()` clears active/pending state, starts hunting, connects to configured target rank or a weighted shuffled batch of monitors, starts auth handshakes, clears old queued messages, cancels version requests with `session_reset`, and renews subscriptions. On auth success, `_finish_hunting()` installs `active_con`, sends queued messages, resends commands, flushes logs, moves auth state, and records global id. `tick()` drives reconnect hunting, subscription renewals for non-stateful-sub monitors, keepalives and keepalive timeout reconnects, log sending, auth ticket checks, rotating-key refreshes, and tell command retries.

Command flow supports normal `MMonCommand` over the active session and directed tell commands. For Octopus and later, tell commands open anonymous direct monitor connections with their own `MonConnection`; legacy monitors force the main session to the target rank/name. Commands are completed asynchronously on the Boost.Asio service executor, and timeout timers cancel outstanding commands.

State includes monmap, config manager values, active and pending monitor connections, tried monitor ranks, auth handlers, rotating secrets, subscriptions, queued messages, outstanding commands, version requests, timers, log state, bootstrap config state, and config callbacks.

## Dependencies and Integration Points

Dependencies include Messenger, Dispatcher, AuthClient/AuthServer, AuthRegistry, KeyRing, RotatingKeyRing, monitor messages, LogClient, AdminSocket, SafeTimer, Boost.Asio, weighted shuffle, mon feature bits, and error categories. It is the shared monitor access layer for clients, daemons, and bootstrap config retrieval.

## Risks and Test Signals

Risks include lock-sensitive callback paths, stale stray monitor messages, global-id changes across reconnects, clearing queued messages on reopen, version request cancellation semantics, tell-command retry limits, auth method fallback, rotating-key renewal frequency and clock skew, passthrough monmap ownership, and config callback execution outside `monc_lock`. Tests should cover hunt success/failure, weighted rank selection, monmap epoch update clearing `tried`, msgr2 reconnect decisions, auth bad-method fallback, shutdown cancellation, command timeout and directed command errors, keepalive reconnects, subscription renewals, config bootstrap, version request replies, and `monc_errc` conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonClient.h -->
# sources/distributed-fs/ceph/src/mon/MonClient.h

## Purpose

`MonClient.h` declares Ceph's monitor client abstraction and its per-connection auth helper. It is the public surface for acquiring monmaps/config, authenticating, sending monitor commands, managing monitor subscriptions, serving authorizers, and exposing monitor connectivity state to daemons and clients.

## Important APIs, Types, and Functions

`MonConnection` owns one monitor `ConnectionRef`, auth state, global id, and optional queued tell command. It exposes v1/v2 auth request and response helpers plus session state queries. `MonClientPinger` is a standalone dispatcher/auth client for isolated monitor ping operations. `monc_errc` defines async errors for shutdown, session reset, missing rank/name, timeout, and monitor unavailability.

`MonClient` derives from `Dispatcher`, `AuthClient`, `AuthServer`, and `AdminSocketHook`. Public APIs include `init()`, `shutdown()`, `build_initial_monmap()`, `get_monmap()`, `get_monmap_and_config()`, `ping_monitor()`, `send_mon_message()`, `reopen_session()`, auth/key methods, subscription methods, monmap accessors, `build_authorizer()`, async `start_mon_command()` overloads, Context-based command wrappers, async `get_version()`, `with_monmap()`, and config callback registration.

## Control Flow and State

The header separates active monitor session state (`active_con`) from hunting state (`pending_cons`, `tried`). It stores auth state, timer state, subscription state, waiting messages, outstanding command map, version request map, bootstrap config state, and config callback hooks. Async command and version APIs use Boost.Asio completion handlers and consign work guards so completions remain valid.

## Dependencies and Integration Points

Dependencies include Boost.Asio, Messenger/Dispatcher, MonMap, MonSub, AdminSocket, Timer, config, auth client/server classes, keyrings, command messages, and Ceph contexts. Consumers use this class across client mount, daemon startup, monitor command execution, config delivery, and service-to-service authentication.

## Risks and Test Signals

The API mixes synchronous waits, lock-protected state, and asynchronous completions. Tests should validate callback completion on shutdown, Context wrapper conversion, directed command target parsing, subscription locking, `with_monmap()` lock usage, auth-server authorizer handling, and public accessors while hunting or stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonCommand.h -->
# sources/distributed-fs/ceph/src/mon/MonCommand.h

## Purpose

`MonCommand.h` defines the serializable monitor command descriptor used for command help, compatibility checks, manager-provided command registration, forwarding behavior, and permissions. It is a small but persistent wire/store contract for command metadata.

## Important APIs, Types, and Functions

`MonCommand` contains `cmdstring`, `helpstring`, `module`, `req_perms`, and `flags`. Flags include `FLAG_NOFORWARD`, `FLAG_OBSOLETE`, `FLAG_DEPRECATED`, `FLAG_MGR`, `FLAG_POLL`, `FLAG_HIDDEN`, and combined `FLAG_TELL`. Methods include flag helpers, `encode()/decode()`, `dump()`, `generate_test_instances()`, `encode_bare()/decode_bare()`, compatibility comparison, semantic predicates (`is_tell`, `is_noforward`, `is_obsolete`, `is_deprecated`, `is_mgr`, `is_hidden`), array/vector encoders with uint16 counts, and `requires_perm()`.

## Control Flow and State

The normal encoder wraps the bare command fields plus flags. Bare encoding includes a removed `availability` string for backward compatibility. Array/vector encoders write all bare records first and then all flags for struct version 2; older decoders default flags to zero. `requires_perm()` tests whether a command requires a permission character from `req_perms`.

## Dependencies and Integration Points

Dependencies are minimal: strings, formatter, and Ceph encoding. `MgrMonitor` stores manager command descriptions using this type and marks active mgr commands with `FLAG_MGR`. Monitor command routing and help generation use the flags to hide commands, block forwarding, mark deprecation, and distinguish tell/asok command behavior.

## Risks and Test Signals

Risks are count truncation above `uint16_t`, losing the backward-compatible availability field, flag loss when decoding older structures, and compatibility comparisons ignoring help text and flags intentionally. Tests should cover single and vector encode/decode, old struct decode default flags, `FLAG_TELL` predicate behavior, permission checks, and command compatibility matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonCommand.h -->
