# sources/distributed-fs/openafs/src/WINNT/afsclass/c_ident.h

## Purpose

`c_ident.h` declares `IDENT`, the typed handle used by AfsClass callers to refer to cached AFS objects without holding direct object pointers.

## Important APIs, Types, and Functions

`IDENTTYPE` enumerates supported object types. Public methods expose type predicates, refcount, reopen methods for each object kind, hierarchy getters, name/ID getters, user-param accessors, global enumeration, and static find helpers for servers, aggregates, filesets, users, and groups. Private members store canonical names, volume ID, user pointer, refcount, global hash list, and hash keys.

## Control Flow

The header defines a value-handle contract backed by a global registry. Callers use `LPIDENT` to reopen objects on demand; object classes create or find identifiers and increment reference counters when exposing them.

## State and Persistence Behavior

Identifiers are process-local state. They mirror object names and IDs and can survive object refreshes, but they are not durable across process restarts.

## Dependencies and Integration Points

The header depends on `afsclass.h`, `VOLUMEID`, `HENUM`, `LPHASHLIST`, and friend access from every major object class.

## Risks and Edge Cases

Manual refcounting is separate from C++ object lifetime and easy to misuse. Because identifiers contain copied names, all rename/move paths must call `Update` after modifying fields that affect hash keys.

## Test Signals

Compile tests should validate public ABI and friend usage. Runtime tests should validate find/open behavior for all types, refcount observations, and hash updates after rename/move.
