# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/DelegatingReadOnlyInodeStore.java

## Purpose
`DelegatingReadOnlyInodeStore` is a forwarding wrapper for read-only access to an underlying mutable `InodeStore`. It lets callers expose only the `ReadOnlyInodeStore` surface while delegating all reads to the underlying store.

## Important APIs and Types
- Implements `ReadOnlyInodeStore`.
- Holds `InodeStore mDelegate` supplied by the constructor.
- Forwards inode lookup, child ID lookup/listing, child lookup, `hasChildren`, `allEdges`, `allInodes`, and `close`.

## Control Flow
Every method is a thin pass-through to the delegate. The wrapper does not expose write APIs even though the delegate is mutable.

## State and Persistence
The class owns no durable metadata. State and persistence live in the delegated store.

## Dependencies and Integration Points
Sits between callers needing a `ReadOnlyInodeStore` and concrete mutable stores such as heap, Rocks, or cache-backed stores. It depends on inode metadata types and `ReadOption`.

## Risks and Edge Cases
- Correctness depends on the delegate being non-null and having the intended lifecycle; the constructor does not perform a null check.
- Closing the wrapper closes the delegate; wrapper owners must avoid double-close surprises if the delegate is shared.

## Test Signals
Tests should use a fake delegate to verify every method forwards arguments and return values, including close and testing-only set accessors.
