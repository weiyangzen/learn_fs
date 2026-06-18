# sources/distributed-fs/ceph-client/tools/perf/util/dsos.h

## Purpose
This header defines the `struct dsos` collection contract for perf machine/map code. It provides a lock-protected dynamic array of DSO references plus APIs for insertion, lookup, iteration, build-id reporting, and module/kernel-specific discovery.

## Important APIs And Types
`struct dsos` contains an `rw_semaphore`, `struct dso **dsos`, count, allocation size, and sorted flag. Public functions cover lifecycle, raw and locked add, lookup by name/id, find-or-create by id, build-id scanning/printing, marking all DSOs as hit, module DSO find/create, kernel DSO lookup, and read-locked iteration callbacks.

## Control Flow And Integration
Machine code initializes a `dsos` collection, adds DSOs as maps/build-id events are processed, finds existing DSOs during mmap synthesis or sample resolution, and tears the collection down with `dsos__exit()`. The implementation owns DSO references while entries remain in the collection.

## State And Persistence
The collection keeps process-local in-memory DSO references only; it does not persist to disk. The sorted flag is part of the lookup invariant and is invalidated by name/id mutations through DSO setters.

## Risks And Test Signals
Risks are around lock discipline and callback behavior under read locks. Tests should verify add/find semantics, cleanup releases references, sorted flag restoration after mutation, and safe behavior when iteration callbacks stop early.
