# sources/cloud-native/containerd/core/metadata/boltutil/context.go

## Purpose

This file provides context helpers for carrying an existing bbolt transaction. Metadata code uses it to compose multiple store operations inside one transaction.

## Important APIs, Types, and Functions

`WithTransaction(ctx, tx)` returns a context containing the transaction under a private key. `Transaction(ctx)` retrieves the `*bolt.Tx` and a boolean.

## Control Flow

The functions are simple context value set/get operations. Type assertion ensures only `*bolt.Tx` values are returned.

## State and Persistence Behavior

The transaction pointer is request-scoped context state. Persistence depends on the transaction owner committing or rolling back outside this helper.

## Dependencies and Integration Points

It depends on `context` and bbolt. The metadata `view` and `update` helpers consume this context state, and tests use it to perform store operations inside explicit transactions.

## Risks and Edge Cases

Context values do not manage transaction lifetime or writability. Passing a closed or rolled-back transaction will fail later. This pattern should not be used across goroutines unless transaction safety is understood.

## Test Signals

Tests should verify retrieval of stored transactions, absence behavior, type safety, and successful metadata operations composed through a context transaction.
