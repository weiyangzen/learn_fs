# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/exportcl.h

## Purpose
`exportcl.h` defines debug-only textual keys for exporting or describing OpenAFS cell objects. The keys cover cells, servers, services, partitions, volumes, principals, replica policy, and group membership.

## Important APIs, Types, And Functions
There are no functions or types. Under `#ifdef DEBUG`, it defines `TEXT(...)` constants such as `eckCELL`, `eckSERVER`, `eckSERVICE`, `eckAGGREGATE`, `eckFILESET`, `eckADDRESS`, service status keys, partition capacity keys, volume quota/time keys, replication policy keys, principal lifetime/key keys, and group/member/owner keys.

## Control Flow
No executable control flow exists. The header is a shared constant table for debug/export code outside this file set.

## State And Persistence
No runtime state is stored here. The constants imply a serialized field vocabulary for debug exports, but actual persistence is handled by consumers.

## Dependencies And Integration Points
The file depends on Windows/TCHAR `TEXT()` macros and only emits definitions for debug builds. It integrates with any debug-only cell export code that needs stable property names.

## Risks And Test Signals
Risks are low but include schema drift between these keys and export/import consumers. Test signals are debug-build compile coverage and export output checks for server, service, aggregate, fileset, principal, and group records.
