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
