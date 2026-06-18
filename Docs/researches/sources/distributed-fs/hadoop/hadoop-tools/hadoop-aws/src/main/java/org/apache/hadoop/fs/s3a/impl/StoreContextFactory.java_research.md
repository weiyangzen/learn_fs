# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContextFactory.java

## Purpose
`StoreContextFactory` abstracts creation of `StoreContext` instances, including capture of current audit span where needed.

## Important APIs and Types
It defines one method: `StoreContext createStoreContext()`.

## Control Flow
Consumers call the factory during store construction or when fresh operation-specific context is needed. Implementations decide what runtime state to capture.

## State and Persistence
The interface has no state. Implementations may snapshot current filesystem/audit state into new context objects.

## Dependencies and Integration Points
It is used by `S3AStoreBuilder` and `S3AStoreImpl`; implementations are usually provided by `S3AFileSystem` or tests.

## Risks and Edge Cases
Returning contexts with stale audit spans, missing executors, or inconsistent request factories will affect every downstream operation.

## Test Signals
Tests should verify factories capture expected audit context and produce contexts with all required dependencies.
