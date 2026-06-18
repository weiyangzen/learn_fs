# sources/distributed-fs/seaweedfs/weed/filer/mount_peer_registry.go

## Purpose

`mount_peer_registry.go` implements an in-memory registry of active mount servers. It supports the first tier of mount peer chunk sharing by letting mounts heartbeat their address/locality to the filer and list currently alive peers.

## Important APIs, Types, and Functions

`MountPeerRegistry` holds a lock, map of peer address to entries, and injectable clock. `MountPeerInfo` is the public listing record. `NewMountPeerRegistry`, `Register`, `List`, `Len`, and `Sweep` are the public operations. Constants cap entries at 10,000 and TTL at one hour.

## Control Flow

`Register` rejects empty addresses, normalizes non-positive TTL to 60 seconds, caps large TTLs, creates or renews an entry under a write lock, and rejects new entries when at capacity while still allowing renewals. `List` takes an RLock, filters expired entries without deleting them, and returns public info. `Sweep` takes a write lock and deletes expired entries.

## State and Persistence Behavior

All registry state is process-local and lost on filer restart. It stores peer address, data center, rack, expiry, and last-seen time. It deliberately does not store per-file or per-chunk state.

## Dependencies and Integration Points

The file depends only on `sync` and `time`. It integrates with mount registration/list RPCs and peer chunk-sharing code that ranks peers by locality.

## Risks and Edge Cases

Expired entries remain in memory until `Sweep`, so sweep cadence matters under churn. Capacity rejection is silent. Locality strings are not validated. The registry is not replicated across filers and should be treated as advisory.

## Test Signals

Tests should cover registration, renewal, expiry filtering, sweep eviction counts, TTL default/cap behavior, empty address rejection, capacity limit, and concurrent list/register/sweep under race detection.
