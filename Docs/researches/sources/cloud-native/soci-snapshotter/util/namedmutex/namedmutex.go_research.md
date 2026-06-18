# sources/cloud-native/soci-snapshotter/util/namedmutex/namedmutex.go

## Purpose
`namedmutex.go` defines a tiny package-level primitive, `NamedMutex`, that gives callers independent `sync.Mutex` instances keyed by string names. It is intended for coordinating work on per-resource keys without serializing all callers through one global mutex.

## Important APIs, Types, and Functions
`type NamedMutex` owns `muMap map[string]*sync.Mutex`, `refMap map[string]int`, and a guard mutex `mu`. `Lock(name string)` lazily initializes maps, creates a per-name mutex, increments the reference count, releases the guard mutex, and then locks the per-name mutex. `Unlock(name string)` retrieves the per-name mutex, decrements and possibly deletes the maps entries, releases the guard mutex, and finally unlocks the per-name mutex.

## Control Flow, State, and Persistence
All state is in memory. The guard mutex serializes map creation and reference-count updates. Reference counts include waiters as soon as they call `Lock`, so a per-name mutex is not deleted while other goroutines are waiting on it. No persistence or external IO is involved.

## Dependencies and Integration Points
The only dependency is Go `sync`. The type is reusable anywhere in the snapshotter that needs keyed exclusion.

## Risks and Test Signals
`Unlock` assumes the name was previously locked; unlocking an unknown name will dereference a nil mutex or mutate a nil map. The code also has no direct test in this subset. The reference-count approach is the key safety signal: deleting occurs before the actual unlock, but waiting goroutines already hold a reference count, so they retain the pointer they will lock.
