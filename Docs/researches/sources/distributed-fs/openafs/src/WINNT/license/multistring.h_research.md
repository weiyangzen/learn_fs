# sources/distributed-fs/openafs/src/WINNT/license/multistring.h

## Purpose

`multistring.h` declares the custom multistring helper used by the Windows license conversion tool. It is separate from NetIDMgr's `mstring.h` and uses `TCHAR`/`LPTSTR` plus an explicit separator character.

## Important APIs, types, and functions

Declared APIs are `mstralloc`, `mstrfree`, `mstrwalk`, `mstrlen`, `mstrcount`, `mstrstr`, `mstrcat`, and `mstrdel`.

## Control flow

The header has no runtime flow. Its comments document the expected operations: allocate/free, iterative progression, length including separators/nulls, entry count, substring membership, append without duplicate checking, and removal.

## State and persistence behavior

The caller owns the multistring pointer and passes it to the implementation for mutation. There is no global state declared here.

## Dependencies and integration points

This header assumes Windows/TCHAR types are already available; `main.cpp` includes `windows.h` before it. It is used only by the license converter in this work item.

## Risks and edge cases

Because the header does not include `windows.h` itself, include ordering matters. The API names are generic and can collide with other multistring utilities if included broadly. Allocation/free pairing with the implementation's `GlobalAlloc`/`GlobalFree` must be respected.

## Test signals

Compile tests should include it after `windows.h`. Behavioral tests belong to `multistring.cpp` and should verify caller-visible pointer mutation and separator semantics.
