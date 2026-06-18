# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/NoopUfsAbsentPathCache.java

## Purpose
`NoopUfsAbsentPathCache` is a disabled implementation of `UfsAbsentPathCache`. It satisfies the cache interface while intentionally recording no absent-path information.

## Important APIs, Types, and Functions
The implementation provides no-op `processAsync(AlluxioURI, List<Inode>)`, `addSinglePath(AlluxioURI)`, and `processExisting(AlluxioURI)`. `isAbsentSince(AlluxioURI, long)` always returns `false`.

## Control Flow, State, and Persistence
There is no runtime or persistent state. Every mutating call returns immediately and every query says the path is not known absent, forcing callers to consult UFS or other metadata rather than trusting an absent-path cache.

## Dependencies and Integration Points
The class implements `UfsAbsentPathCache` and is used when absent-path caching is disabled or intentionally bypassed. It accepts the same path and inode-prefix arguments as the asynchronous cache implementation but ignores them.

## Risks
Using this implementation removes an optimization and may increase UFS metadata calls. Behavior is safe but conservative: it cannot return stale absent positives because it never returns positives.

## Test Signals
Tests should verify all operations are no-ops and `isAbsentSince()` always returns false. Integration tests can assert that disabling absent-path caching selects this implementation and still produces correct namespace behavior.
