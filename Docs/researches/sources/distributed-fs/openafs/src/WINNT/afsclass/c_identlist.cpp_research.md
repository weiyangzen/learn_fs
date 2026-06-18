# sources/distributed-fs/openafs/src/WINNT/afsclass/c_identlist.cpp

## Purpose

`c_identlist.cpp` implements `IDENTLIST`, a small hash-list-backed container for unique `LPIDENT` pointers.

## Important APIs, Types, and Functions

Implemented methods are constructor/destructor, `Add`, `Remove`, `RemoveAll`, `CopyFrom`, `GetCount`, `fIsInList`, `FindFirst`, `FindNext`, and `FindClose`.

## Control Flow

Construction allocates a `HASHLIST`. `Add` inserts uniquely, `Remove` removes a pointer, and `RemoveAll` repeatedly removes the first object until empty. `CopyFrom` clears the current list and enumerates another `IDENTLIST`, adding each identifier. Enumeration wraps `HASHLIST` enumeration and returns `LPIDENT` objects without opening backing objects.

## State and Persistence Behavior

The list owns only the container, not the identifiers. It does not adjust `IDENT::m_cRef` and does not persist data.

## Dependencies and Integration Points

It depends on `HASHLIST`, `LPIDENT`, `HENUM`, `New`, and `Delete`. It is a utility for callers that need sets of object identifiers.

## Risks and Edge Cases

Because identifiers are borrowed, entries can become stale if the global registry deletes an `IDENT` while it is in a list. The list does not set a critical section, so thread safety depends on external synchronization. `CopyFrom` does not close the source enumeration explicitly after natural exhaustion.

## Test Signals

Tests should cover duplicate adds, removing absent/present identifiers, copying from another list, empty enumeration, and behavior when the source list is empty.
