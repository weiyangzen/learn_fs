<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConnectionTracker.h -->
# sources/distributed-fs/ceph/src/mon/ConnectionTracker.h

## Purpose
`ConnectionTracker.h` declares the data structures and owner interface for monitor connectivity scoring. It provides the serialized report format exchanged between monitors and persisted locally for election decisions.

## Important APIs, types, and functions
`ConnectionReport` contains rank, current liveness, historical scores, epoch, and epoch version, plus Ceph encode/decode, equality, dumping, and test-instance generation. `DirectedGraph` stores incoming and outgoing edges for netsplit detection. `RankProvider` abstracts the owning monitor's rank and persistence callback.

`ConnectionTracker` exposes peer report ingestion, epoch/version updates, live/dead reports, half-life configuration, total score queries, cleanliness checks, netsplit detection, encode/decode, cached encoded buffer access, reset/rank notifications, formatter dumping, and test-instance generation.

## Control flow
The header documents the intended score update formula and owner callback behavior: score updates bump the version, and version multiples of the persist interval are persisted through `RankProvider`. Election code calls total-score queries only when the local rank is known.

## State and persistence behavior
`ConnectionTracker` owns all score state in memory and is serializable through `WRITE_CLASS_ENCODER(ConnectionTracker)`. The owner pointer is not serialized; decoded trackers are data snapshots used for import or persistence restore. `clear_peer_reports()` resets reports while preserving the current rank in `my_reports`.

## Dependencies and integration points
The header depends on Ceph encoding and basic monitor types. It is included by `ElectionLogic` and `Elector`; election messages carry encoded tracker data and the monitor store persists the encoded tracker under the elector's keys.

## Risks and edge cases
Decoded snapshots have no owner, so methods that trigger persistence should not be called on decoded peer snapshots. Copy construction preserves owner and context pointers, which is useful for stable election snapshots but requires care if copied across lifetimes. Rank-indexed maps must be updated when monmap ranks change or monitors are removed.

## Test signals
Encoder tests should use generated instances for `ConnectionReport` and `ConnectionTracker`. Integration tests should verify snapshots imported from messages do not persist, owner-backed trackers do persist, and rank reset/change/removal paths keep `is_clean()` true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConnectionTracker.h -->
