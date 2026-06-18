# sources/distributed-fs/eos/mgm/tgc/SpaceToTapeGcMap.cc

## Purpose
`SpaceToTapeGcMap.cc` implements a mutex-protected map from EOS space name to per-space `TapeGc` instances. It is the ownership and dispatch container used by `MultiSpaceTapeGc`.

## Important APIs, Types, And Functions
Implemented methods include constructor, `createGc()`, `destroyAllGc()`, `getGc()`, `getStats()`, `getSpaces()`, `toJson()`, and `startGcWorkerThreads()`.

## Control Flow
`createGc()` validates a non-empty space, locks, rejects duplicates, constructs a `TapeGc`, stores it in a `unique_ptr`, and returns a reference. `getGc()` locks and returns the referenced GC or throws `UnknownEOSSpace`. `getStats()` snapshots stats from each non-null GC. `toJson()` locks while serializing each GC's JSON and enforces maxLen after each child. `startGcWorkerThreads()` locks and starts every non-null per-space worker.

## State And Persistence
State is in-memory: MGM interface reference, mutex, and `std::map<std::string, std::unique_ptr<TapeGc>>`. Destroying all GCs clears the map and stops ownership of per-space state.

## Dependencies And Integration Points
The map owns `TapeGc` objects, exposes `TapeGcStats`, throws `MaxLenExceeded`, and is used directly by `MultiSpaceTapeGc` for lifecycle, event dispatch, population, stats, and FSCTL diagnostics.

## Risks And Edge Cases
`getGc()` returns a reference after releasing the mutex, so concurrent `destroyAllGc()` can invalidate that reference unless higher-level lifecycle locking prevents it. `toJson()` holds the map mutex while calling each `TapeGc::toJson()`, which may be expensive and can create lock-order risks if `TapeGc` calls back. Space names are written into JSON without escaping. Returning references to owned objects requires careful start/stop ordering.

## Test Signals
Existing `SpaceToTapeGcMapTests` cover creation, duplicate/unknown errors, stats, JSON, and worker startup. Additional tests should cover empty space names, concurrent get/destroy expectations, JSON escaping for unusual space names, and maxLen propagation.
