# sources/distributed-fs/ceph/src/mds/InoTable.h

## Purpose

`InoTable.h` declares the MDS inode-number allocation table. It is an `MDSTable` subclass named `inotable` whose encoded state is the set of unused inode IDs for an MDS rank, with a projected copy used to reserve IDs for journaled operations before they commit.

## Important APIs, Types, And Functions

Constructors initialize the base `MDSTable` with table name `"inotable"` and persistence enabled. Allocation methods are `project_alloc_id()`, `apply_alloc_id()`, `project_alloc_ids()`, and `apply_alloc_ids()`. Release methods are `project_release_ids()` and `apply_release_ids()`.

Replay methods are `replay_alloc_id()`, `replay_alloc_ids()`, `replay_release_ids()`, and `replay_reset()`. Repair/tooling methods are `repair()`, `is_marked_free()`, `intersects_free()`, `skip_inos()`, `force_consume()`, and `force_consume_to()`.

`encode_state()` writes version 2 and encodes only `free`. `decode_state()` reads `free` and initializes `projected_free` to match. Standalone `encode()`/`decode()` wrappers support dencoder. `dump()` and `generate_test_instances()` support diagnostics and serialization tests.

## Control Flow And Data Flow

The header exposes a two-phase allocation contract: callers first project changes against `projected_free`, journal the mutation, then apply the same changes to `free` after commit. Replay methods rebuild both sets from journal events. Tooling methods can consume IDs directly when repairing or adjusting a table offline or in controlled online repair paths.

`intersects_free()` is a safety query for detecting whether an external interval overlaps available IDs. `force_consume()` and `force_consume_to()` are explicitly documented for tools, not normal allocation.

## State And Persistence Behavior

`free` is committed persistent state. `projected_free` is runtime state rebuilt from `free` after decode/reset and changed by outstanding projected operations. Only `free` is encoded, so all in-flight projected operations must be represented by journal state or otherwise resolved during recovery.

Versioning is inherited from `MDSTable`; the implementation advances `version` for applied mutations and `projected_version` for projections/replay.

## Dependencies And Integration Points

Dependencies include `MDSTable`, `MDSRank`, `inodeno_t`, `interval_set`, Ceph buffer encoding, and `Formatter`. Integration points include inode creation, journal replay, table reset/recovery, MDSRank table lifecycle, dencoder tests, and repair code that reconciles discovered inode usage with free ranges.

## Risks And Edge Cases

The class relies on callers respecting active-state and projection/apply ordering. Explicit allocation of an ID outside `projected_free`, insufficient free ranges for a requested batch, or applying a different interval than projected can desynchronize committed and projected state. Since only `free` persists, crashes between projection and apply must be recoverable through journal replay.

The repair helpers bypass normal journaling assumptions if used incorrectly. They should be limited to tooling or guarded online repair paths. `is_marked_free()` returns true if either committed or projected state contains the ID, which is conservative for detecting conflicts but can surprise callers expecting only committed state.

## Test Signals

Tests should cover encode/decode compatibility, projected versus committed state after every project/apply pair, replay reset and replay mutation paths, repair guard on version mismatch, interval intersection results, and tool helpers consuming only intended ranges.
