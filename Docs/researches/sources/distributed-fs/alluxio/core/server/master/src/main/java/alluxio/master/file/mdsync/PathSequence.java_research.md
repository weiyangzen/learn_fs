# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/PathSequence.java

Purpose: immutable value object representing a loaded half-open path range from start to end.

Important APIs and types: constructor accepts start and end `AlluxioURI`s. Package-private `getStart` and `getEnd` expose bounds. `equals` and `hashCode` compare both endpoints.

Control flow: `DefaultSyncProcess` returns loaded ranges in `SyncProcessResult`; `BatchPathWaiter` merges them and uses them to decide when a path has been synced far enough for callers to proceed.

State and persistence behavior: in-memory coordination state only. It represents progress through persistent metadata reconciliation but is not itself stored.

Dependencies and integration points: depends on `AlluxioURI` ordering and equality. Integrates with `SyncProcessResult` and `BatchPathWaiter`.

Risks: bounds semantics are implicit; callers treat start inclusive and end exclusive. If URI ordering differs from UFS listing order, range coverage can be wrong.

Test signals: tests should cover equality, hash code, range merge behavior in `BatchPathWaiter`, and boundary path wait decisions.
