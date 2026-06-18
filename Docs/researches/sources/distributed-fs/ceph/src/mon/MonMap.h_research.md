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
