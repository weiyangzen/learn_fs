# sources/distributed-fs/eos/mgm/tgc/SpaceToTapeGcMap.hh

## Purpose
Declares `SpaceToTapeGcMap`, the MGM-side owner of per-space tape-aware garbage collectors. It is the registry that turns an EOS space name into a `TapeGc` instance and exposes aggregate statistics, space names, JSON dumping, and worker-thread startup.

## Important APIs, types, and functions
The constructor stores an `ITapeGcMgm&` used to construct each `TapeGc`. `createGc()` validates a non-empty space, creates exactly one collector per space, and throws `GcAlreadyExists` on duplicates. `destroyAllGc()` clears all owned collectors. `getGc()` returns a reference or throws `UnknownEOSSpace`. `getStats()`, `getSpaces()`, `toJson()`, and `startGcWorkerThreads()` expose operational state across all collectors.

## Control flow
Callers create collectors as spaces become tape-GC-enabled, then start all workers once configured. Runtime operations lock the map, look up the requested space, and either delegate to the stored `TapeGc` or build aggregate results.

## State and persistence behavior
State is in-memory only: `m_gcs` maps space names to `std::unique_ptr<TapeGc>`, protected by `m_mutex`. There is no direct persistence; the durable behavior is delegated to MGM namespace/config state through each `TapeGc` and its `ITapeGcMgm` interface.

## Dependencies and integration points
Depends on `ITapeGcMgm`, `TapeGc`, and `TapeGcStats`. It is part of the `EOSTGC` namespace and integrates with code that tracks which EOS spaces should run tape-aware disk-replica eviction.

## Risks and test signals
`getGc()` returns a reference after releasing the map lock, so external lifetime must ensure no concurrent `destroyAllGc()` invalidates that reference. `toJson()` manually writes JSON keys without escaping space names. Tests should cover duplicate creation, empty-space errors, unknown lookups, concurrent create/get/destroy behavior, JSON max-length exceptions, and worker startup idempotence through the underlying collectors.
