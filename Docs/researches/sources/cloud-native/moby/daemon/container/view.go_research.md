# sources/cloud-native/moby/daemon/container/view.go

## Purpose
Implements the daemon's in-memory, transactional read model for containers. `ViewDB` stores immutable deep-copied `Container` objects and name reservations in a HashiCorp `go-memdb` database, then exposes read-only `View` snapshots used by container listing, lookup, and name-resolution paths.

## Important APIs, Types, And Functions
- `Snapshot` embeds API `container.Summary` and adds query/filter fields such as `CreatedAt`, `StartedAt`, `Pid`, `Running`, `Paused`, `Managed`, port sets, health, and isolation.
- `NewViewDB`, `Save`, `Delete`, `ReserveName`, and `ReleaseName` are the mutating store API.
- `Snapshot`, `All`, `Get`, `GetID`, and `GetAllNames` are read APIs backed by read transactions.
- `GetByPrefix` resolves unique ID prefixes and reports empty, missing, or ambiguous prefixes with typed `errdefs` errors.
- Custom memdb indexers add null-terminated exact keys and prefix keys for container IDs and name associations.

## Control Flow
Writers call `withTxn`, mutate the containers or names tables, and commit or abort atomically. Readers acquire a memdb read transaction through `Snapshot()` and resolve objects through indexed queries. `transform` converts a `Container` into an API-facing `Snapshot`, copying selected network endpoint fields, port mappings, mount summaries, labels, host config details, command strings, health state, and image manifest descriptor data.

## State And Persistence
This file is memory-only. Persistence comes from containers checkpointing deep copies into this replica elsewhere. The key invariant is that stored containers must be immutable copies because `transform` does not take the container lock.

## Dependencies And Integration Points
Depends on `go-memdb`, daemon `container.Container`, API container/network types, and Moby `errdefs`. It integrates with container checkpointing (`CheckpointTo`), name reservation flows, container list/filter APIs, and ID-prefix lookup paths.

## Risks And Edge Cases
Mutating a stored container copy would race readers because snapshots are intentionally lock-free. `Delete` removes associated names even when the container record is absent, which is useful for cleanup but depends on correct container IDs. `transform` logs and skips invalid host port ranges rather than failing a list request. Network and label maps are partially cloned; future fields need the same immutability discipline.

## Test Signals
Covered by `view_test.go`: save/delete, listing, exact lookup, name reservation conflicts and snapshot isolation, health propagation, prefix ambiguity, and prefix lookup benchmarks.
