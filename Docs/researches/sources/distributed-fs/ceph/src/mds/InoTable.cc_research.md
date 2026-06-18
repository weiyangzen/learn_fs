# sources/distributed-fs/ceph/src/mds/InoTable.cc

## Purpose

`InoTable.cc` implements the MDS rank inode-number allocation table. It tracks free inode numbers for one rank, supports projected allocations/releases for journaled operations in flight, applies committed changes, replays journal events after restart, and offers repair/tooling helpers for consuming inode numbers that were incorrectly marked free.

## Important APIs, Types, And Functions

`reset_state()` initializes this rank's inode range to `[(rank + 1) << 40, (rank + 2) << 40)`, stores it in `free`, and mirrors it into `projected_free`.

Single-ID allocation uses `project_alloc_id(id=0)` and `apply_alloc_id(id)`. A zero projected ID means allocate `projected_free.range_start()`. Batch allocation uses `project_alloc_ids(interval_set<inodeno_t>& ids, int want)` and `apply_alloc_ids(interval_set<inodeno_t>& ids)`. Release uses `project_release_ids()` and `apply_release_ids()`.

Replay APIs are `replay_alloc_id()`, `replay_alloc_ids()`, `replay_release_ids()`, and `replay_reset()`. They mutate both `free` and `projected_free` and set `projected_version = ++version` so replay catches up without outstanding projections.

Tooling/repair APIs are `skip_inos(inodeno_t count)`, `is_marked_free()`, `intersects_free()`, `repair(inodeno_t id)`, and `force_consume_to(inodeno_t ino)`. `dump()` emits both projected and committed free ranges, and `generate_test_instances()` supports dencoder coverage.

## Control Flow And Data Flow

Normal allocation flow is two-phase. Request handling calls a `project_*` method while the table is active; this removes IDs from `projected_free` and bumps `projected_version`. Once the journaled mutation commits, `apply_*` removes the same IDs from committed `free` and bumps `version`. Release mirrors this in reverse by inserting intervals into projected then committed state.

Replay flow consumes journal records after restart. Allocation replay checks the committed `free` set, logs cluster errors if journaled IDs are not free, subtracts only the intersection for batch replay, and advances both committed and projected versions. Release replay inserts IDs into both sets.

Repair flow refuses to repair while `projected_version != version`, because in-flight projections could conflict. If safe, it asserts the inode is marked free, erases it from both sets, and advances versions. `force_consume_to()` skips all free IDs from the current first free ID through a specified inode if that inode lies at or beyond the first free value.

## State And Persistence Behavior

The persistent state is the committed `free` interval set encoded by `InoTable::encode_state()` in the header. `decode_state()` restores `free` and sets `projected_free = free`. The projected set is runtime state for outstanding journal operations, not separately persisted.

`version` and `projected_version` come from `MDSTable` and track committed versus projected mutations. Replay deliberately synchronizes them after each journal event. `reset_state()` depends on the MDS rank value inherited from `MDSTable`.

## Dependencies And Integration Points

The implementation depends on `MDSTable`, `MDSRank`, `interval_set<inodeno_t>`, debug logging, and `mds->clog` for replay consistency errors. `MDSRank` constructs `InoTable`; journal event code calls project/apply/replay; `Server` and inode creation paths allocate IDs; `CInode` repair code uses `repair()` when a discovered inode number was marked free.

## Risks And Edge Cases

Allocation assumes `projected_free` is non-empty; `range_start()` on an empty set would fail. `project_alloc_id(id)` does not check that an explicit ID is in `projected_free` before erasing. `project_alloc_ids()` loops until `want` is satisfied and likewise assumes enough space exists. `force_consume_to()` computes `ino + 1 - first`, so extremely large `ino` values near the type limit need care.

Replay of inconsistent journal state logs errors but still advances versions, subtracting only the intersection for batch allocation. That avoids crashing recovery but can leave evidence only in cluster logs. The rank-based 40-bit range is static; any change to rank allocation semantics must preserve old table compatibility.

## Test Signals

Tests should verify reset range boundaries per rank, project/apply version movement, batch allocation across interval boundaries, release reinsertion and coalescing, encode/decode round trips, replay behavior for valid and invalid allocations, `repair()` refusal with outstanding projections, `force_consume()` and `force_consume_to()` behavior, and dump output for committed versus projected ranges.
