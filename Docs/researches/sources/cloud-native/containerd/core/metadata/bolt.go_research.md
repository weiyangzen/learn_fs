# sources/cloud-native/containerd/core/metadata/bolt.go

## Purpose

This file abstracts Bolt transaction execution and lets metadata operations reuse a transaction already stored on context. It is the bridge between context-scoped transactions and the DB's read/write transaction API.

## Important APIs, Types, and Functions

`Transactor` defines `View` and `Update`. `view(ctx, db, fn)` runs `fn` inside a read transaction, reusing `boltutil.Transaction(ctx)` when present. `update(ctx, db, fn)` similarly reuses a context transaction but rejects non-writable transactions.

## Control Flow

Both helpers check the context first. Without a context transaction they call `db.View` or `db.Update`. With a transaction, `view` directly invokes the callback. `update` checks `tx.Writable()` and returns a wrapped `ErrTxNotWritable` if the context transaction is read-only.

## State and Persistence Behavior

The helpers do not persist data themselves, but they control transaction boundaries for all metadata stores. Reusing a context transaction allows multi-object operations to be atomic across store calls.

## Dependencies and Integration Points

They depend on `boltutil.Transaction`, bbolt transactions, and bbolt error definitions. Metadata container/content/image/lease/snapshot stores call them for their CRUD operations.

## Risks and Edge Cases

A writable transaction in context bypasses `DB.Update`'s mutation callback and lock behavior unless the caller created it through the DB carefully. A read-only context transaction passed to update fails. Callers must ensure context transaction lifetime outlives the operation and is not used concurrently unsafely.

## Test Signals

Tests should cover transaction reuse, starting new transactions when absent, read-only transaction rejection, nested metadata calls inside a single update transaction, and callback/dirty behavior when operations bypass `DB.Update`.
