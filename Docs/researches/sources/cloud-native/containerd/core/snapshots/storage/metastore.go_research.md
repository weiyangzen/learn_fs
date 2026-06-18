# sources/cloud-native/containerd/core/snapshots/storage/metastore.go

## Purpose
Defines the transaction wrapper and lifecycle for a BoltDB-backed snapshot metadata store.

## APIs, Flow, State, Dependencies, Risks, And Tests
`Transactor` abstracts commit/rollback. `Snapshot` returns active/view metadata: kind, numeric ID, and ordered parent IDs. `Opt` customizes bbolt options. `MetaStore` stores db path, mutex, lazy-open database pointer, and options. `NewMetaStore` records dbfile and options. `TransactionContext` lazily opens the DB, begins a read or write transaction, and injects it into context with `transactionKey`. `WithTransaction` runs a callback and commits only if writable and callback succeeds; otherwise it rolls back, joining callback and transaction errors. `Close` closes the DB if open.

Persistent state is the Bolt database file; transactions are stored only in context. The mutex protects lazy opening and closing. Dependencies include bbolt, snapshots, log, context, errors, and sync.

Integration points are storage operations in `bolt.go` and snapshotter plugins that wrap metadata and filesystem operations atomically. Risks include callers forgetting rollback/commit when using `TransactionContext` directly, context key coupling, close while transactions are active, and callback side effects that must be cleaned after commit failure. Test signals are metastore suite and transaction open/close benchmarks.
