# sources/distributed-fs/openafs/src/WINNT/afsclass/c_agg.h

## Purpose

`c_agg.h` declares `AGGREGATE`, the AfsClass abstraction for a server partition and its fileset cache. It exposes aggregate status, identity, parent navigation, user parameters, and fileset lookup/enumeration APIs.

## Important APIs, Types, and Functions

`AGGREGATESTATUS` carries partition ID, total space, free space, and allocated quota. Public methods include `Close`, invalidation methods, `RefreshStatus`, `RefreshFilesets`, `GetIdentifier`, `OpenCell`, `OpenServer`, `GetName`, `GetDevice`, `GetID`, `GetStatus`, `GetGhostStatus`, user-param accessors, `OpenFileset`, and `FilesetFind*`. Private members include parent identifiers, partition strings, ghost and partition IDs, stale flags, fileset `HASHLIST`, hash keys, and cached status.

## Control Flow

The header establishes a lazy-refresh contract: status and filesets are refreshed only when their stale flags are set. Enumeration methods use `HENUM` handles and require a matching close. Object lifetime follows the wider AfsClass model where `Open*` increments the shared library critical-section/reference context and `Close` releases it.

## State and Persistence Behavior

`AGGREGATE` owns no durable storage. Its state is a memory cache of server partition data and child `FILESET` objects, invalidated by explicit calls and rebuilt from VOS.

## Dependencies and Integration Points

The class is a friend of `CELL`, `SERVER`, `FILESET`, and `IDENT`, allowing those classes to manipulate ghost flags, child lists, and cached status. It integrates with `LPIDENT`, `LPHASHLIST`, `LPHASHLISTKEY`, `VOLUMEID`, and `AGGREGATESTATUS`.

## Risks and Edge Cases

Friend-heavy access makes invariants distributed across `CELL`, `SERVER`, and `FILESET`. `size_t` is used for storage counts and quotas, so ABI assumptions can vary by target bitness. Callers must not hold enumeration objects across refresh/deletion.

## Test Signals

Compile and ABI checks should validate `AGGREGATESTATUS` layout. Behavioral tests should verify stale flag transitions, hash lookup by fileset name and ID, parent navigation, and deletion notification cascades.
