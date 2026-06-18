# Research: subset-b-006925 monitor command, map, request, and subscription files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonCommands.h -->
# sources/distributed-fs/ceph/src/mon/MonCommands.h

## Purpose

`MonCommands.h` is a deliberately unguarded command-definition inventory for Ceph monitor command descriptions. It is intended to be included multiple times with different definitions of `COMMAND`, `COMMAND_WITH_FLAG`, or related macros so callers can generate command tables, help text, command parsing metadata, module routing data, permissions, and visibility/forwarding flags from one authoritative list. The file is data-as-C++-preprocessor rather than conventional executable code.

The leading comment documents the command signature DSL consumed by the Python `ceph` frontend and by monitor-side command parsing. Each command signature encodes literals, typed arguments, repeat counts, optional flags, allowed values, good-character constraints, and positional versus non-positional separation. The monitor ultimately sees parsed command JSON as `cmdmap_t`/`cmd_vartype` data and dispatches by prefix to the relevant monitor service.

## Important APIs, types, and command surfaces

Important macro-facing APIs are:

- `COMMAND(signature, helpstring, modulename, req_perms)` for ordinary commands.
- `COMMAND_WITH_FLAG(signature, helpstring, modulename, req_perms, FLAG(...))` for hidden, deprecated, obsolete, manager-routed, polling, tell/asok, and no-forward commands.
- `DEFAULT_GOODCHARS`, `FS_NAME_GOODCHARS`, and `CLASS_GOODCHARS`, which constrain several CephString arguments.
- `FLAG(NONE)`, `FLAG(NOFORWARD)`, `FLAG(OBSOLETE)`, `FLAG(DEPRECATED)`, `FLAG(MGR)`, `FLAG(POLL)`, `FLAG(HIDDEN)`, and `FLAG(TELL)` as documented command metadata.

The file covers monitor-visible command families for:

- Placement group and generic OSD queries near the top, such as `pg map`, `pg repeer`, and `osd last-stat-seq`.
- Authentication commands implemented by `AuthMonitor`, including export/get/list/import/add/rotate/caps/rm and pending-key workflows.
- Core monitor commands implemented by `Monitor`, including status, health, log, quorum status, node listing, ok-to-stop checks, `tell`, monitor metadata, monitor versions, and monitor store scrub/compact.
- CephFS/MDS commands implemented by `MDSMonitor` and FS command handlers, including filesystem creation/removal/reset, flags, feature and compatibility manipulation, mirroring, rename, swap, and MDS fail/repair/remove operations.
- Monmap commands, including `mon dump`, `mon getmap`, `mon add`, `mon rm`, feature listing/setting, rank/address/weight mutation, msgr2 enablement, election strategy, disallowed leaders, CRUSH-style monitor location, and stretch-mode tiebreaker operations.
- OSD and CRUSH commands, including map dumps, metadata, CRUSH bucket/rule/class/weight-set changes, OSD flags, releases, pg-upmap controls, blocklist commands, OSD creation/removal/purge/lost workflows, and pool creation/deletion/parameter/application/stretch/tiering commands.
- `config-key`, manager, central config, and NVMe-oF gateway commands.
- Legacy tell/asok aliases used during upgrade windows before all monitor command handling moved to the newer path.

## Control flow and integration points

This header has no runtime control flow on its own. Control flow is imposed by the includer. In practice, a monitor command-description generator includes this file with `COMMAND` macros expanded into command descriptor records; command dispatch code then uses the generated descriptors to validate CLI/API input, enforce permissions, and route parsed commands to service-specific handlers.

The `modulename` and `req_perms` fields are integration points with Cephx capability checks. The module also directs implementation ownership: for example auth commands go to `AuthMonitor`, monmap commands to `MonmapMonitor`, OSD commands to `OSDMonitor`, config-key commands to `KVMonitor`, manager commands to `MgrMonitor`, and core monitor/tell commands to `Monitor` or admin-socket handling.

The flag field changes dispatch behavior:

- `TELL` commands are hidden/no-forward commands for daemon admin-socket style handling.
- `MGR` commands route through ceph-mgr rather than being handled by monitors.
- `DEPRECATED` and `OBSOLETE` influence help visibility and frontend warnings/compatibility.
- `POLL` documents high-frequency status commands.
- `NOFORWARD` prevents forwarding through the leader path.

## State and persistence behavior

This file does not own persistent state. It defines the public and semi-public command surface that mutates persistent monitor service maps elsewhere. Several declared commands are persistence-sensitive because they change Paxos-backed monitor state:

- `mon feature set`, `mon set-rank`, `mon set-addrs`, `mon set-weight`, and stretch/election commands mutate monmap state.
- OSD map, CRUSH map, pool, erasure-code-profile, blocklist, and release commands mutate OSDMonitor state.
- Auth commands mutate the auth database.
- Config and config-key commands mutate monitor config stores.
- MDS/FS commands mutate FSMap/MDSMap state.

Because this file is the validation metadata source, any mismatch between a signature here and handler expectations can reject valid operations, accept malformed requests, or mis-shape `cmdmap_t` values before persistence code runs.

## Dependencies

The header depends on macro definitions supplied by includers. It also depends conceptually on:

- `cmdparse` type names and validators such as `CephInt`, `CephFloat`, `CephString`, `CephIPAddr`, `CephEntityAddr`, `CephPgid`, `CephOsdName`, `CephChoices`, `CephBool`, `CephUUID`, and `CephPrefix`.
- Monitor service handlers that recognize the literal `prefix` produced from each command signature.
- Frontend command parsers that consume `get_command_descriptions` output.
- Capability enforcement that interprets the module and permission string fields.

## Risks and edge cases

- The file intentionally has no include guard. Accidental ordinary inclusion without the right macro setup will either fail to compile or produce duplicated definitions.
- The command-signature DSL is whitespace-sensitive. Missing spaces between adjacent string fragments or extra malformed descriptors can change parser behavior.
- There is at least one suspicious descriptor typo: `osd pool application get` uses `req=fasle` for `pool`, which looks like a misspelling of `req=false`; depending on parser strictness, this may make the argument required by default or be rejected/ignored.
- Several commands use historical aliases (`auth print_key`, `mon remove`, `osd blacklist`, `config-key put/del/list`, `osd pool delete`, tier remove aliases). Changing or deleting them can break upgrade, automation, or user scripts.
- Destructive commands rely on boolean confirmation fields such as `yes_i_really_mean_it`; signature mistakes can weaken or over-tighten guardrails before service-side checks.
- Very long `CephChoices` lists for pool variables and flags can drift from handler-supported variables, producing hard-to-debug CLI/API skew.
- Module/permission mismatches are security-sensitive because they determine which Cephx caps authorize a command.

## Test signals

Useful test coverage should include:

- Command-description generation tests that include this file with descriptor-producing macros and verify parsing of representative signatures from each module.
- CLI parser tests for optional arguments, repeated `n=N` arguments, `CephBool` non-positional behavior, `--` separation, `goodchars`, and long `CephChoices` lists.
- Negative tests for deprecated/hidden/tell/no-forward/manager flags and command visibility.
- Handler-dispatch tests ensuring every declared prefix maps to an implementation path and that handler-required cmdmap keys match signature names and types.
- Upgrade/compatibility tests for deprecated aliases and legacy tell/asok commands.
- Security tests that validate module permission strings against expected Cephx caps for read-only versus mutating commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonCommands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonMap.cc -->
# sources/distributed-fs/ceph/src/mon/MonMap.cc

## Purpose

`MonMap.cc` implements monitor map serialization, deserialization, initialization, address normalization, rank calculation, display/dump helpers, health checks, and bootstrap discovery. Together with `MonMap.h`, it defines the persisted representation that clients and monitors use to locate monitor daemons, establish quorum membership, determine monitor ranks, gate monitor features, and handle election/stretch-mode metadata.

The implementation is highly compatibility-sensitive. It emits different wire/storage layouts depending on peer feature bits such as `CEPH_FEATURE_MONNAMES`, `CEPH_FEATURE_MONENC`, and `SERVER_NAUTILUS`, while decoding older struct versions into the current in-memory shape.

## Important APIs, types, and functions

Key `mon_info_t` functions:

- `mon_info_t::encode()` writes versioned monitor metadata. It downgrades to legacy single-address encoding when the peer lacks Nautilus/server address-vector support.
- `mon_info_t::decode()` reads versions through v6, filling optional `priority`, `weight`, `crush_loc`, and `time_added` only when present.
- `print()`, `dump()`, and `generate_test_instances()` expose human, formatter, and encode/decode test data paths.

Key `MonMap` functions:

- `calc_legacy_ranks()` sorts monitors by legacy/front address and name, preserving the historic rank order for old maps.
- `encode()` has legacy layouts for peers without monitor names, without `MONENC`, and without Nautilus, then a current v9 layout including ranks, min release, removed ranks, election strategy, disallowed leaders, stretch mode, tiebreaker, and stretch marked-down mons.
- `decode()` accepts legacy compact forms, reconstructs `mon_info` from older `mon_addr` maps, infers `min_mon_release` when absent, and refreshes `addr_mons`.
- `write()` and `read()` persist a complete encoded monmap to a file through `ceph::buffer::list`.
- `add()` inserts a unique monitor, timestamps it, updates ranks based on feature gates, and rebuilds address lookup.
- `print_summary()`, `print()`, `dump()`, and `dump_summary()` drive CLI and JSON-style output.
- `_add_ambiguous_addr()` normalizes ambiguous monitor addresses into legacy and/or msgr2 addresses based on type, port, and mkfs mode.
- `init_with_addrs()`, `init_with_ips()`, `init_with_hosts()`, `init_with_config_file()`, `init_with_dns_srv()`, and `build_initial()` build an initial monmap from CLI/config/context/DNS sources.
- `set_initial_members()` filters and fills the map for a configured initial monitor member list.
- `check_health()` emits `MON_LOCATION_NOT_SET` warnings when stretch mode is enabled but monitor CRUSH locations are missing.

## Control flow

Encoding starts by checking connection feature compatibility. If the peer lacks `CEPH_FEATURE_MONNAMES`, the map is encoded as a v1 vector of ranked `entity_inst_t` records named `mon.N`. If the peer lacks `MONENC`, the map is encoded as v2 with a string-to-legacy-address map. If the peer has `MONENC` but lacks `SERVER_NAUTILUS`, a v5 structure carries legacy address maps plus features and `mon_info`. Current peers get v9, where address vectors, ranks, feature sets, release gates, removed ranks, election strategy, disallowed leaders, and stretch-mode state are all explicit.

Decoding reverses this through `DECODE_START_LEGACY_COMPAT_LEN_16(9, 3, 3, p)`. Legacy v1 vectors become numeric monitor names and `mon_addr` entries; versions below v5 synthesize `mon_info_t` records from `mon_addr`; versions below v6 recalculate ranks; versions below v7 infer the release from persistent mon features; versions below v9 clear stretch-mode state.

Bootstrap initialization follows a precedence chain. Non-Crimson code checks `mon_host_override`, context-provided monitor addrs, `monmap` file, configured `fsid`, `mon_host`, config-file `mon.*` sections, DNS SRV, and finally errors if no monitors are found. Crimson follows the same general idea asynchronously using Seastar futures, starting from `mon_host_override` or `monmap`, then `mon_host`, config sections, and DNS SRV.

Address normalization in `_add_ambiguous_addr()` is central to msgr1/msgr2 compatibility. Typed addresses keep their type, defaulting ports as needed. Untyped legacy-port addresses become legacy; untyped IANA-port addresses become msgr2; no-port addresses expand to both protocols unless mkfs mode combines them into one addrvec; arbitrary untyped ports prefer msgr2 and optionally add a legacy sibling.

## State and persistence behavior

The in-memory state persisted by current monmaps includes:

- `fsid`, `epoch`, `last_changed`, and `created`.
- `persistent_features` and `optional_features`, whose union is required for quorum operation.
- `mon_info`, each record containing name, public address vector, priority, weight, CRUSH location, and time added.
- `ranks` and `removed_ranks`.
- `min_mon_release`.
- Election behavior: `strategy` and `disallowed_leaders`.
- Stretch-mode state: enabled flag, tiebreaker monitor, and marked-down monitor names.

`add()`, header-defined `remove()`, `rename()`, `set_rank()`, `set_addrvec()`, and `set_weight()` mutate in-memory map state. They rely on callers, usually monitor services, to bump epochs, update timestamps, and propose/persist through Paxos where appropriate. The file-level `write()` path encodes with `CEPH_FEATURES_ALL`, while client/server wire encoding is feature-negotiated.

`addr_mons` is a derived lookup map rebuilt by `calc_addr_mons()` and not independently persisted. `ranks` are derived for pre-Nautilus-compatible maps but explicit for Nautilus-feature maps.

## Dependencies

This implementation depends on Ceph core encoding macros, `ceph::buffer::list`, address parsing helpers, DNS resolution, `ConfigProxy`, `CephContext`, release/feature helpers, `Formatter`, `health_check_map_t`, `entity_addr_t`, `entity_addrvec_t`, `uuid_d`, and `utime_t`. Crimson builds additionally depend on Seastar file and DNS APIs plus `crimson::common::ConfigProxy`.

Integration points include:

- `MonmapMonitor` command handling for monmap mutation.
- monitor bootstrap paths that call `build_initial()`.
- client/monitor messenger setup that consumes address vectors and ranks.
- election code that consumes `strategy`, `disallowed_leaders`, ranks, and stretch-mode data.
- health reporting that consumes stretch-mode location requirements.
- encode/decode infrastructure and generated test instances used by Ceph serialization tests.

## Risks and edge cases

- Wire compatibility branches are easy to break. Removing legacy `mon_addr` or single-address fallbacks can strand older clients or mixed-version monitors.
- `mon_info_t::encode()` deliberately emits a synthesized legacy address when only v2 addresses exist; old clients may receive a valid-looking but unusable address. That is intentional but still operationally risky.
- Rank behavior differs before and after the Nautilus mon feature. Pre-feature maps derive rank from sorted address/name order; post-feature maps preserve explicit rank order. Mutation code must use the same gate consistently.
- `_add_ambiguous_addr()` can create `name-legacy` sibling monitors outside mkfs mode. Automation that assumes one configured endpoint equals one monitor name must account for this.
- `add()` asserts uniqueness of names and every address in the addrvec. Bad caller validation can crash debug/assert builds rather than returning an error.
- `set_initial_members()` creates dummy legacy IPv4 addresses with unique nonces for missing members; these are placeholders and can be confusing in diagnostics if not replaced.
- `init_with_config_file()` parses priority/weight with `std::stoul` and stores in `uint16_t` without an explicit range check beyond conversion success.
- `init_with_dns_srv()` has different error semantics across Crimson and non-Crimson paths: Crimson ignores DNS lookup failures inside futures until final size checks, while non-Crimson returns errors through `errout`.
- Stretch mode only warns on missing monitor location; it does not repair or block by itself in this file.

## Test signals

Relevant tests should exercise:

- Encoding/decoding across legacy v1/v2/v5 and current v9 layouts, including feature-negotiated output.
- `generate_test_instances()` round trips for empty maps, empty addresses, priority/weight, CRUSH location, and time-added fields.
- Rank recalculation versus explicit rank preservation under feature gates.
- Add/remove/rename/set-rank/set-addrvec/set-weight invariants and `addr_mons` refresh.
- Parsing and normalization of typed, untyped, default-port, legacy-port, IANA-port, no-port, and addrvec monitor endpoints in both mkfs and non-mkfs modes.
- Bootstrap precedence for override, context addresses, monmap file, `mon_host`, config sections, DNS SRV, and no-monitor failures.
- Stretch-mode health warning behavior for monitors with and without `crush_loc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonMap.h -->
# sources/distributed-fs/ceph/src/mon/MonMap.h

## Purpose

`MonMap.h` declares the monitor map data model used throughout Ceph monitor bootstrap, monitor-client discovery, quorum membership, election ranking, feature gating, and monmap persistence. It defines `mon_info_t`, the per-monitor record, and `MonMap`, the cluster-level map containing all monitors and associated compatibility/election/stretch metadata.

The header contains both declarations and a meaningful amount of inline mutating/query logic, so callers use it as the primary API for monmap membership and lookup.

## Important APIs, types, and fields

`mon_info_t` fields:

- `name`: monitor id without the `mon.` prefix.
- `public_addrs`: `entity_addrvec_t` public endpoints used by clients and monitors.
- `priority` and `weight`: election/connectivity preference metadata.
- `time_added`: timestamp set when added to the map.
- `crush_loc`: CRUSH hierarchy-style location map used by stretch mode and failure-domain reasoning.

`mon_info_t` APIs include versioned `encode()`, `decode()`, `print()`, `dump()`, and `generate_test_instances()`.

`MonMap` primary fields:

- Versioning and identity: `epoch`, `fsid`, `last_changed`, `created`.
- Membership: `mon_info`, derived `addr_mons`, explicit `ranks`, and `removed_ranks`.
- Feature state: `persistent_features`, `optional_features`, and `get_required_features()`.
- Upgrade gate: `min_mon_release`.
- Election state: `election_strategy` with `CLASSIC`, `DISALLOW`, and `CONNECTIVITY`, plus `strategy` and `disallowed_leaders`.
- Stretch mode: `stretch_mode_enabled`, `tiebreaker_mon`, and `stretch_marked_down_mons`.

Important inline APIs:

- Size and quorum helpers: `size()`, `min_quorum_size()`, `get_epoch()`, `set_epoch()`, `get_fsid()`.
- Membership mutation: `add()`, inline `add(name, addrv, priority, weight)`, `remove()`, `rename()`, `set_rank()`, `set_addrvec()`, and `set_weight()`.
- Lookup helpers: `contains(name)`, `contains(entity_addr_t)`, `contains(entity_addrvec_t)`, `get_name(rank/address/addrvec)`, `get_rank(name/address/addrvec)`, `get_addr_name()`, and `get_addrs(name/rank)`.
- Rank/address maintenance: `calc_legacy_ranks()` and inline `calc_addr_mons()`.
- Persistence and formatting: `encode()`, `decode()`, `write()`, `read()`, `print()`, `print_summary()`, `dump()`, and `dump_summary()`.
- Bootstrap helpers: `build_initial()`, `set_initial_members()`, and protected init helpers for address strings, hostnames, config sections, DNS SRV, and monmap files.
- Health: `check_health()`.

## Control flow

Most header-defined control flow preserves consistency between `mon_info`, `ranks`, and `addr_mons`.

`remove()` asserts the monitor exists, records the removed rank, erases leader restrictions for that name, erases the monitor, then either removes the explicit rank entry for Nautilus-feature maps or recalculates legacy ranks for older-feature maps. It rebuilds `addr_mons` at the end.

`rename()` copies and erases a `mon_info` entry, updates the embedded name, rewrites the explicit rank slot or recalculates legacy ranks, and refreshes address lookup.

`set_rank()` validates the named monitor and target range, then moves the monitor name inside the `ranks` vector.

Lookup functions first use exact maps where possible (`addr_mons` for address to name) but also include linear scans for `contains(entity_addr_t)` and `contains(entity_addrvec_t)` to check every stored public address.

Protected bootstrap functions are declared here and implemented differently for Crimson and non-Crimson builds. The public `build_initial()` API is therefore compile-time polymorphic: Seastar future-returning for Crimson and integer errno-returning for classic builds.

## State and persistence behavior

`MonMap` is the in-memory representation that `MonMap.cc` serializes. The header defines which fields are persisted by current encoding and which are derived:

- Persisted current map state includes identity/version timestamps, feature sets, `mon_info`, ranks, release gate, removed ranks, election state, and stretch-mode state.
- `addr_mons` is derived and must be rebuilt after membership/address mutations.
- The required feature set is derived from persistent OR optional feature sets.
- Rank order may be derived in legacy-feature maps and explicit in newer maps.

Mutation helpers do not themselves perform Paxos persistence or epoch/timestamp management. They maintain local consistency and assume higher-level monitor services wrap changes in the appropriate monmap proposal lifecycle.

## Dependencies

The header depends on Ceph core types and forward declarations: `entity_addr_t`, `entity_addrvec_t`, `epoch_t`, `uuid_d`, `utime_t`, `mon_feature_t`, `ceph_release_t`, `health_check_map_t`, `ConfigProxy`, `CephContext` through declarations/implementation, `ceph::Formatter`, and optionally Seastar/Crimson config types.

Integration points include:

- `MonMap.cc` for implementation and encoding details.
- `MonmapMonitor` for cluster monmap updates.
- monitor election logic, which must keep `election_strategy` values synchronized with `ElectionLogic.h`.
- monitor bootstrap and client monitor discovery.
- health reporting for stretch-mode monitor locations.
- command handling from `MonCommands.h` for monmap mutation commands.

## Risks and edge cases

- Many mutators use `ceph_assert` rather than returning errors. Caller-side validation is required before invoking them with user-provided names, ranks, or addresses.
- `addr_mons` can become stale if new mutators are added without calling `calc_addr_mons()`.
- `remove()` inserts removed ranks and supports arbitrary counts, even though comments say usually one rank is removed at a time; consumers must handle multiple entries.
- `ranks` and `mon_info` must stay equal in size under explicit-rank maps. The code asserts this after several operations.
- `get_name(rank)` and `get_addrs(rank)` assert rank bounds; external code should validate ranks first.
- `contains(entity_addrvec_t)` treats any overlapping address as containment, not whole-vector equality.
- `set_weight()` changes weight without recalculating ranks or elections locally; higher layers must decide when changes affect leader selection.
- The enum values must remain synchronized with `ElectionLogic.h`; changing either side independently can corrupt persisted or command-provided election strategy interpretation.

## Test signals

Header-level behavior is best tested with:

- Unit tests for every inline mutator preserving `mon_info`, `ranks`, and `addr_mons` invariants.
- Tests for `min_quorum_size()` with explicit total and default current size.
- Address-vector containment semantics where only one address overlaps.
- Error-return tests for `set_rank()` absent monitor and invalid rank, plus success reordering.
- Feature-gated tests for `remove()` and `rename()` under legacy-rank and explicit-rank behavior.
- Compile coverage for both Crimson and non-Crimson declarations.
- Tests verifying election strategy numeric constants remain aligned with election logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonOpRequest.h -->
# sources/distributed-fs/ceph/src/mon/MonOpRequest.h

## Purpose

`MonOpRequest.h` defines the tracked operation wrapper used by monitor code to carry a received `Message` through dispatch, service handling, Paxos waits, forwarding, command processing, and callbacks. It extends `TrackedOp` so monitor operations can be observed in slow-op/historic-op dumps with event timings and request descriptors.

It also defines `C_MonOp`, a callback base class that retains a `MonOpRequestRef` and marks completion, retry, or cancellation events before delegating to subclass-specific `_finish()`.

## Important APIs, types, and fields

`MonOpRequest` inherits from `TrackedOp` and is reference-counted through `boost::intrusive_ptr` as `MonOpRequest::Ref` / `MonOpRequestRef`.

Important fields:

- `Message *request`: the underlying monitor message. The destructor releases it with `put()`.
- `RefCountedPtr session`: retained monitor session private data, usually a `MonSession`.
- `ConnectionRef con`: source connection captured from the message.
- `bool forwarded_to_leader`: diagnostic flag set by `mark_forwarded()`.
- `op_type_t op_type`: coarse request classification.
- `utime_t dequeued_time`: declared but not manipulated in this header.

Important methods:

- Event markers: `mark_dispatch()`, `mark_wait_for_quorum()`, `mark_zap()`, `mark_forwarded()`, `mark_svc_event()`, and service-specific helpers for log, OSD map, PG map, MDS map, auth, and Paxos events.
- Request/session access: `get_req<T>()`, `get_req()`, `get_req_type()`, `get_connection()`, `get_session()`, and `set_session()`.
- Source checks: `is_src_mon()`.
- Type setters/getters: `set_type_service()`, `set_type_monitor()`, `set_type_paxos()`, `set_type_election_or_ping()`, `set_type_command()`, `get_op_type()`, and `is_type_*()` helpers.
- Debug output overrides: `_dump()` and `_dump_op_descriptor()`.

`C_MonOp` APIs:

- `finish(int r)` marks `"callback canceled"`, `"callback retry"`, or `"callback finished"` for `-ECANCELED`, `-EAGAIN`, or `0` before calling `_finish(r)`.
- `mark_op_event()` lets subclasses add arbitrary events.
- `_finish(int r)` is pure virtual for concrete callback behavior.

## Control flow

`MonOpRequest` construction is private and intended for `OpTracker` creation. The constructor initializes `TrackedOp` with the message receive timestamp when available or `ceph_clock_now()` otherwise, stores the raw request pointer, captures the connection, and reads the connection private pointer as the monitor session.

During monitor processing, dispatchers and services call event marker methods to append timestamped entries to the underlying `TrackedOp`. `mark_forwarded()` also flips `forwarded_to_leader` for dump output. `set_type_*()` calls classify the operation so monitor diagnostics can distinguish service, monitor, election, Paxos, and command paths.

Dumping opens an `events` array, locks the inherited event list, emits each event and duration to the next event or from initiation to the last event, then emits request info such as sequence, source-is-monitor, source instance, and forwarded flag. `_dump_op_descriptor()` delegates to the underlying message `print()`.

`C_MonOp::finish()` is a callback control-flow hook: it annotates the retained operation based on the completion code and then calls subclass `_finish()`.

## State and persistence behavior

This file does not persist cluster state. Its state is operational telemetry and request lifetime management:

- It keeps the underlying `Message` alive until the wrapper is destroyed.
- It retains the monitor session and connection for authorization, routing, and diagnostics.
- It records an event timeline used by operation tracking, slow-op reporting, historic-op dumps, and admin diagnostics.
- It records whether the request was forwarded to the leader and its high-level type.

Because `MonOpRequest` wraps monitor messages that may trigger Paxos updates, losing or misclassifying the wrapper affects observability and routing decisions but not direct persistence serialization.

## Dependencies

The header depends on `TrackedOp`, `RefCountedObj`, `Context`, `Formatter`, `Session.h`, `Connection.h`, and `Message.h`. It is included widely by monitor services such as `Monitor`, `PaxosService`, `Paxos`, `Elector`, `OSDMonitor`, `MDSMonitor`, `AuthMonitor`, `LogMonitor`, `ConfigMonitor`, `KVMonitor`, `MgrMonitor`, and health/NVMe monitor code.

Integration points:

- `OpTracker` is a friend and constructs instances.
- Monitor dispatch uses `MonOpRequestRef` as the common request handle.
- Paxos wait callbacks commonly derive from or use `C_MonOp`.
- Admin/historic operation dump code consumes `_dump()` and `_dump_op_descriptor()`.

## Risks and edge cases

- The destructor unconditionally calls `request->put()`. The constructor accepts `Message *req` and several methods handle null, but `_dump()`, `_dump_op_descriptor()`, and the destructor assume a non-null request. Creation should not pass null in production.
- `_dump()` uses `request->get_source_inst()` and event timing while holding the event lock for event iteration. Code changes should avoid introducing lock inversions with formatter or message code.
- `is_src_mon()` uses bitwise `get_peer_type() & CEPH_ENTITY_TYPE_MON`, relying on entity type bit conventions.
- Session capture happens at construction from connection private data. If connection private state changes later, the wrapper may retain the earlier session unless `set_session()` is called.
- Event strings are free-form. Inconsistent naming reduces diagnostic value and can break tooling that expects known event labels.
- `op_type_t` is diagnostic but may be used for filtering; new dispatch paths should set it consistently.

## Test signals

Useful tests include:

- Construction through `OpTracker` with messages that have and lack receive stamps, verifying initiated time selection.
- Request lifetime tests that ensure `put()` occurs exactly once when the wrapper is released.
- Event marker tests for dispatch, quorum wait, zap, forwarded, service-specific labels, and `C_MonOp::finish()` status mapping.
- Dump tests validating event duration fields, request source fields, forwarded flag, and op descriptor output.
- Session/connection tests for `get_session()`, `set_session()`, and `is_src_mon()`.
- Type classification tests covering every `set_type_*()` and `is_type_*()` helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonOpRequest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonSub.cc -->
# sources/distributed-fs/ceph/src/mon/MonSub.cc

## Purpose

`MonSub.cc` implements `MonSub`, the monitor-client subscription state machine used to request, renew, acknowledge, advance, reload, and cancel subscriptions to monitor-maintained data streams. It is used by `MonClient` to track wanted maps or service updates and to decide when a new `MMonSubscribe` request should be sent.

The implementation separates unsent/new subscriptions from sent subscriptions and advances each subscription start epoch as updates arrive.

## Important APIs and functions

- `have_new()` returns whether there are pending unsent subscriptions in `sub_new`.
- `need_renew()` compares `ceph::coarse_mono_clock::now()` with `renew_after`.
- `renewed()` marks a subscription request as sent by merging old sent subscriptions with new ones, swapping into `sub_sent`, clearing `sub_new`, and setting `renew_sent` if no renewal is already in flight.
- `acked(interval)` handles `MMonSubscribeAck` intervals, primarily for legacy monitors, by setting the next renewal point to half the ack interval after `renew_sent`.
- `reload()` copies all sent subscriptions not already pending back into `sub_new`, typically after reconnect or monitor session reset.
- `got(what, have)` advances or removes a subscription when a map/update version is received.
- `want(what, start, flags)` requests a subscription if no identical pending or sent subscription already exists.
- `inc_want(what, start, flags)` requests only if the desired start is greater than the existing start.
- `unwant(what)` cancels pending and sent state for a subscription key.

## Control flow

The normal flow starts with `want()` or `inc_want()`, which creates/updates an entry in `sub_new` and returns `true` when a send is needed. `MonClient` can then call `get_subs()` from the header and send an `MMonSubscribe`. After sending, `renewed()` moves all active subscription state to `sub_sent`. When the monitor replies with an ack interval, `acked()` schedules the next renewal at half the interval.

When the client receives an update, `got()` looks first in `sub_new`, then in `sub_sent`. If the current requested `start` is less than or equal to the received `have` version, one-time subscriptions are erased; persistent subscriptions advance to `have + 1` so future requests ask only for newer data.

On reconnect or resubscribe events, `reload()` repopulates `sub_new` from `sub_sent` for any subscription not already pending. Cancellation through `unwant()` erases both maps.

## State and persistence behavior

`MonSub` state is in-memory client-side subscription bookkeeping:

- `sub_new`: requested but unsent subscriptions.
- `sub_sent`: subscriptions already sent to a monitor.
- `renew_sent`: time the current renewal request was sent.
- `renew_after`: next time a renewal should be sent.

No state is persisted to disk or Paxos. The `start` values inside `ceph_mon_subscribe_item` are durable only for the lifetime of the client object and are reconstructed by callers after reconnect or process restart.

## Dependencies

The implementation depends on:

- `MonSub.h` for class declaration.
- `ceph::coarse_mono_clock`, `ceph::coarse_mono_time`, and `ceph::make_timespan`.
- `ceph_mon_subscribe_item` and `CEPH_SUBSCRIBE_ONETIME` from Ceph protocol headers.
- `MonClient`, which owns a `MonSub`, sends `MMonSubscribe`, handles `MMonSubscribeAck`, and calls `got()` when map versions arrive.

## Risks and edge cases

- `renewed()` only sets `renew_sent` if it is currently zero. Multiple sends before an ack keep the original send time, which is intentional for one in-flight renewal but can skew renewal timing if send/ack handling is changed.
- `acked(interval)` schedules renewal at `interval / 2.0`; very small or zero intervals can make `need_renew()` true immediately.
- `got()` checks `sub_new` before `sub_sent`, so a pending changed subscription takes precedence over an older sent subscription.
- `want()` considers an identical sent subscription sufficient and returns false. If the connection was lost but `reload()` was not called, callers may incorrectly believe no send is needed.
- `inc_want()` never lowers a start epoch. That avoids duplicate older updates but can prevent callers from re-requesting history through this API.
- Map ordering by string key is deterministic but there is no explicit concurrency protection; callers should use it from the owning client thread/context.

## Test signals

Useful tests include:

- `want()` idempotency for identical pending and sent subscriptions, and update behavior for changed start/flags.
- `renewed()` merge behavior when both `sub_new` and `sub_sent` contain entries.
- `acked()` scheduling with normal, small, and zero intervals.
- `got()` advancement for persistent subscriptions and erasure for one-time subscriptions in both new and sent maps.
- `reload()` repopulation without overwriting already pending entries.
- `inc_want()` behavior for higher, equal, and lower start versions.
- `unwant()` removing both pending and sent entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonSub.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonSub.h -->
# sources/distributed-fs/ceph/src/mon/MonSub.h

## Purpose

`MonSub.h` declares the `MonSub` class, a compact in-memory subscription tracker used by Ceph monitor clients. It records which monitor data subscriptions are newly requested, which have already been sent, what version each subscription should start from, and when renewals are due.

The class is part of the monitor client protocol machinery around `MMonSubscribe` and `MMonSubscribeAck`.

## Important APIs, types, and fields

Public APIs:

- `have_new()` reports whether unsent subscriptions exist.
- `get_subs()` returns a copy of `sub_new` for message construction.
- `get_start(what)` returns the requested start version, preferring pending new state over sent state and returning `0` if absent.
- `need_renew()` checks whether renewal time has passed.
- `renewed()` moves new requests into sent state.
- `acked(interval)` updates renewal scheduling after monitor acknowledgment.
- `got(what, version)` advances/removes subscription state after receiving data.
- `reload()` makes sent subscriptions pending again.
- `want(what, start, flags)` requests an exact subscription.
- `inc_want(what, start, flags)` requests a higher start version only.
- `unwant(what)` cancels a subscription.

Private state:

- `sub_sent`: map of subscription name to `ceph_mon_subscribe_item` that has been sent.
- `sub_new`: map of subscription name to unsent `ceph_mon_subscribe_item`.
- `renew_sent`: coarse monotonic time when renewal was sent.
- `renew_after`: coarse monotonic deadline for the next renewal.

## Control flow

Callers request subscriptions through `want()` or `inc_want()`. If either returns true, `have_new()` becomes true and `get_subs()` exposes the pending map for a subscribe message. After the message is sent, `renewed()` transitions pending entries to `sub_sent`. After acknowledgment, `acked()` schedules the next renewal. As updates arrive, `got()` advances the start version or removes one-time entries. Reconnect handling can call `reload()` to resend active subscriptions, and callers use `unwant()` to cancel.

`get_start()` is important for callers deciding the current requested version. It intentionally checks `sub_new` first so a pending update to subscription state overrides older sent state.

## State and persistence behavior

`MonSub` has no persistent storage and does not encode/decode itself. It is volatile protocol state inside `MonClient`. The only durable-ish data it tracks is the next requested `version_t` per subscription while the process is alive.

The class stores maps by subscription key string, and values are protocol structs containing `start` and `flags`. Renewal timing uses monotonic coarse time, avoiding wall-clock adjustments.

## Dependencies

The header depends on:

- `common/ceph_time.h` for coarse monotonic time types.
- `include/ceph_fs.h` for `ceph_mon_subscribe_item` and subscription flags.
- `include/types.h` for `version_t`.
- Standard `map` and `string`.

Integration points include `MonClient.h`, `MonClient.cc`, `MMonSubscribe`, and `MMonSubscribeAck`.

## Risks and edge cases

- `get_subs()` returns a copy by value. That is simple and safe but can be wasteful if many subscriptions are added.
- `renew_after` default initialization relies on default construction of coarse monotonic time; callers should expect initial `need_renew()` behavior to be defined by that zero/default value.
- There is no locking. Use from multiple threads would need external serialization.
- Subscription names are untyped strings, so misspellings create independent subscriptions rather than compile-time failures.
- `get_start()` returning `0` for absent keys means callers must distinguish "not subscribed" from a legitimate start-at-zero request by checking subscription existence through other state if needed.

## Test signals

Header-facing tests should verify:

- `get_start()` precedence for `sub_new` over `sub_sent`.
- `have_new()` and `get_subs()` after request, renewal, reload, and cancel operations.
- Initial renewal behavior before any ack.
- Correct use of `version_t` start values and subscription flags.
- Caller integration with `MonClient` message creation and ack handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/MonSub.h -->
