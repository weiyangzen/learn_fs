# sources/distributed-fs/lizardfs/src/chunkserver/legacy_replicator.h

## Purpose
`legacy_replicator.h` exposes the legacy chunk replication entry points used by background jobs and master command handling.

## Important APIs, Types, and Functions
`legacy_replicator_stats(uint32_t *repl)` drains and resets the replication operation counter. `legacy_replicate(uint64_t chunkid, uint32_t version, uint8_t srccnt, const uint8_t *srcs)` performs a replication from a packed source list. The source list format is documented as `srccnt * (chunkid:64 version:32 ip:32 port:16)`.

## Control Flow
Callers pass a destination chunk ID/version and one or more packed source descriptors. The implementation creates the destination chunk, pulls block data from sources, writes it, and returns a LizardFS status byte.

## State and Persistence Behavior
The header itself has no state. Its implementation persists the replicated chunk on local HDD storage only after successful completion; failed runs attempt cleanup.

## Dependencies and Integration Points
It includes platform and integer types. `masterconn.cc` uses this API indirectly through job-pool functions for `MATOCS_REPLICATE`. `legacy_replicator.cc` depends on `hddspacemgr` and socket/protocol helpers.

## Risks and Edge Cases
The packed `srcs` buffer has no length parameter in this API, so caller-side validation of `srccnt` and packet length is mandatory. It only represents legacy standard chunk replication; newer EC/chunk-type-aware replication is handled elsewhere.

## Test Signals
Tests should verify master packet handlers compute `srccnt` correctly before calling this function and reject malformed lengths. ABI/compile tests should ensure the function remains available for legacy job wrappers.
