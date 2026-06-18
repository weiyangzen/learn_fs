# sources/distributed-fs/openafs/src/WINNT/afsclass/c_ident.cpp

## Purpose

`c_ident.cpp` implements `IDENT`, the process-wide stable identifier registry for cells, servers, services, aggregates, filesets, users, and groups. Identifiers preserve enough names and IDs to reopen the current backing object and carry caller user data.

## Important APIs, Types, and Functions

It implements constructors for every object type, type predicates, `Open*` methods, `Get*` hierarchy methods, name/ID getters, user-param accessors, enumeration, static `Find*` helpers, `RemoveIdentsInCell`, `Update`, and hash key callbacks for type/server, fileset ID, fileset name, and account name.

## Control Flow

`InitClass` lazily creates the global `x_lIdents` hash list and keys. Each constructor extracts canonical names/IDs from the source object and adds the identifier to the global list. `Open*` methods reopen the cell and walk through parent objects to find the current backing object. `FindIdent` selects the fastest key: fileset ID for volume lookups, fileset-name key for certain cross-server searches, or type/server key otherwise. Fileset identity handling is special because volumes can move and read-only replicas can share IDs; aggregate matching is required for probable replicas.

## State and Persistence Behavior

All state is in memory: type, cell/server/service/aggregate/fileset/account strings, volume ID, caller user pointer, and manual reference count. Identifiers persist for the life of the process until removed from the hash list or destroyed, and can outlive a particular backing object.

## Dependencies and Integration Points

The file depends on all object classes, `HASHLIST`, `AfsClass_GenFullUserName`, server name shortening, AfsClass assertion semantics, and direct friend access to object internals.

## Risks and Edge Cases

The registry is global and mostly initialized without setting an explicit critical section in this file, so thread safety depends on `HASHLIST` defaults and higher-level `AfsClass_Enter`. `RemoveIdentsInCell` deletes identifiers while iterating the same list. The account-name hash ignores instance in the key and filters afterward, which is correct but collision-heavy for common names. `FindNext` for identifier enumeration only returns filesets after the first item, which makes general `FindFirst/FindNext` enumeration asymmetric.

## Test Signals

Tests should cover identity reuse after fileset move, read-only replica lookup, user names with instances, group/user name collisions, service/aggregate reopen paths, user-param persistence, refcount increments/decrements by owning objects, and global enumeration.
