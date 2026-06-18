<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/namedmutex/namedmutex.go -->
# sources/cloud-native/stargz-snapshotter/util/namedmutex/namedmutex.go

## Purpose
Implements a keyed mutex that serializes work by string name while allowing unrelated names to proceed concurrently.

## Important APIs, Types, And Functions
- `NamedMutex` holds a map from name to lock entry and a global mutex.
- `Lock(name)` creates or reuses a per-name lock and increments its reference count.
- `Unlock(name)` releases the per-name lock, decrements references, and removes unused entries.

## Control Flow
Lock first protects the map, obtains/creates the named lock entry, increments count, unlocks the map, then locks the named mutex. Unlock checks for an entry, unlocks it, decrements count under the global lock, and deletes the entry at zero.

## State And Persistence
In-memory map of named locks and refcounts only.

## Dependencies And Integration Points
Used by `LayerManager.resolveLayer` to prevent duplicate resolution of the same ref/layer digest.

## Risks And Edge Cases
Unlocking an unknown name is a no-op or error-handled only by code path details, so misuse can hide bugs. Callers must balance lock/unlock exactly. Entries are removed only when refcount reaches zero.

## Test Signals
Expected tests cover same-name serialization, different-name parallelism, refcount cleanup, and balanced unlock behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/namedmutex/namedmutex.go -->
