# sources/distributed-fs/coda/coda-src/util/arrlist.h

## Purpose
Declares the `arrlist` pointer-vector utility and its sequential iterator.

## Important APIs, Types, And Functions
`arrlist` exposes public fields `list`, `maxsize`, and `cursize`, plus `init()`, `Grow()`, constructors, destructor, and `add()`. `arrlist_iterator` stores the target list and previous index and implements `operator()()`.

## Control Flow
Callers create an `arrlist`, append with `add()`, and scan with `arrlist_iterator`. The iterator returns raw stored pointers and stops with `NULL`.

## State And Persistence
The header defines only in-memory state. It has no ownership contract for pointed-to objects and no persistent format.

## Dependencies And Integration Points
This is standalone C++ utility code and is included by code that needs a simple non-template dynamic pointer array.

## Risks
Public mutable fields make invariants easy to break. The iterator contract warns that deletion of the current entry is unsafe. Copying is not prohibited at the type level.

## Test Signals
Compile users against the declarations, verify ABI expectations for public fields, and run append/iteration tests with mutation avoided during scans.
