# sources/distributed-fs/coda/coda-src/util/dict.cc

## Purpose
Implements an abstract dictionary layer on top of `dlist`, adding reference counting and delayed destruction for `assoc` entries plus `assocrefs` arrays of held references.

## Important APIs, Types, And Functions
`dictionary::Add`, `Remove`, `Find`, `Put`, and `Kill` manage entries. `assoc::Hold`, `Release`, and `Suicide` manage reference lifetime. `assocrefs::Attach`, `Detach`, `Kill`, `Index`, and `assocrefs_iterator` manage arrays of references to associations.

## Control Flow
An `assoc` constructor records its dictionary, inserts itself, starts with refcount 1, and is not dying. `Find()` scans the list, compares keys, holds the found object, and returns it. `Put()` releases and nulls a caller reference. `Suicide()` marks an entry dying; the final `Release()` removes it from the dictionary and deletes it. `assocrefs` grows its pointer array, holds attached assocs, and releases or suicides references during detach/kill.

## State And Persistence
State is in-memory reference counts, dying flags, key/value pointers, dictionary membership, and reference arrays. No persistent storage or locking is provided.

## Dependencies And Integration Points
Depends on `dict.h`, `dlist`, and `CODA_ASSERT`. It is intended for old Coda subsystems with object dictionaries and cross-reference sets.

## Risks
The package is explicitly not multithread-capable. `assocrefs::Detach(0)` and `Kill(0)` dereference `Assoc` in the all-case path instead of `assocs[i]`, which is a serious null-pointer bug if used. The base `assoc` destructor asserts, so every concrete derived class must implement a virtual destructor. Array growth zeroing after `realloc` appears to use `max - ActualGrowSize` as a byte offset, which can clear the wrong region.

## Test Signals
Create derived key/value/assoc types, find/put/kill entries, verify delayed deletion after outstanding refs, attach/detach indexed refs, test all-reference operations, and run under sanitizers for null and realloc clearing bugs.
