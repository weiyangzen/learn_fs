# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/PathProperties.java

## Purpose
`PathProperties` is the meta master source of truth for path-level configuration properties. It provides thread-safe read/write access, journals all mutations, computes a hash for configuration cache invalidation, and exposes a journaled delegate state object.

## Important APIs and Types
- Implements `DelegatingJournaled`.
- Uses a `ReadWriteLock` to guard `State mState` and `Hash mHash`.
- `snapshot()` returns `PathPropertiesView` with a deep copy, current hash, and last update time.
- `get()` returns a deep copy of all path-to-property maps.
- `add(Supplier<JournalContext>, String, Map<PropertyKey,String>)` merges properties for a path and journals a full path properties entry.
- `remove(..., Set<String>)` removes selected keys and journals either an updated full path entry or a remove entry.
- `removeAll(...)` removes all properties for a path.
- Nested `State implements Journaled` stores `Map<String, Map<String,String>>`, processes journal entries, resets state, and emits checkpoint journal entries.

## Control Flow
Writers acquire the write lock, derive a copy of the path's current properties, apply the requested mutation, call `State.applyAndJournal`, and mark the hash outdated. Reads acquire the read lock and return copies. Journal replay enters `State.processJournalEntry`, which applies `PathPropertiesEntry` by replacing a path's full map and `RemovePathPropertiesEntry` by deleting the path.

## State and Persistence
The in-memory state is a nested map keyed by path and property name. Persistence uses Alluxio journal entries with checkpoint name `PATH_PROPERTIES`. The class intentionally journals the complete property set for a path after each path mutation, trading write size for simple replay semantics. The hash is computed from path/key/value strings and tracks last update time.

## Dependencies and Integration Points
Integrates with `MetaMaster` path configuration RPCs, `JournalContext`, `Journaled` checkpoint/replay machinery, `PropertyKey`, and configuration hash consumers such as `MetaMasterConfigurationServiceHandler`.

## Risks and Edge Cases
- The implementation assumes path property operations are not highly concurrent; a single read/write lock may become a bottleneck under heavy mutation.
- `getProperties(path)` returns a copy; write paths must journal the modified copy or changes would be lost.
- The hash supplier streams over map entries; deterministic hashing depends on the `Hash` class handling ordering or on callers tolerating hash changes from map iteration order.
- Empty add maps are ignored; removal of missing paths does not journal.

## Test Signals
Tests should cover add merge/overwrite, selective removal, remove-all, no-op empty mutations, deep-copy isolation, hash update after mutations, journal replay, reset, and checkpoint iterator output.
