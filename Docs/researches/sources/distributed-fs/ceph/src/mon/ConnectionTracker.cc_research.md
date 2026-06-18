<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConnectionTracker.cc -->
# sources/distributed-fs/ceph/src/mon/ConnectionTracker.cc

## Purpose
`ConnectionTracker.cc` implements monitor-to-monitor connectivity scoring, peer report exchange, persistence-ready encoding, rank-change cleanup, and netsplit detection. Election code uses these scores to prefer better-connected leaders under the connectivity election strategy.

## Important APIs, types, and functions
`ConnectionTracker::receive_peer_report()` imports newer peer reports by epoch and version. `increase_epoch()` resets local version for a new election epoch, while `increase_version()` updates local report version and periodically asks the owner to persist scores. `report_live_connection()` and `report_dead_connection()` adjust exponentially aged per-peer scores and current liveness. `get_total_connection_score()` sums how peers view a candidate rank. `notify_rank_changed()` and `notify_rank_removed()` rewrite local and peer report rank-indexed maps after monmap changes.

`DirectedGraph` supports `get_netsplit()` by storing incoming/outgoing directed edges. Encoding and diagnostics are implemented by `encode()`, `decode()`, `get_encoded_bl()`, `dump()`, `ConnectionReport::dump()`, and test-instance generators.

## Control flow
Live/dead reports auto-initialize history scores to 1.0, then move scores toward one or zero by `units / (2 * half_life)`, clamp to `[0,1]`, set current liveness, and bump the version. Every `persist_interval` versions, the tracker calls `RankProvider::persist_connectivity_scores()`.

Peer reports are accepted only if their epoch is newer or their version is newer within the same epoch. Encoding is cached in `encoding` and cleared whenever state changes. Netsplit detection copies local reports into `peer_reports`, builds a directed graph of currently connected monitor pairs excluding known down monitors, then returns normalized monitor pairs with no observed bidirectional communication and at least incoming-edge presence.

## State and persistence behavior
The tracker stores `epoch`, `version`, `peer_reports`, `my_reports`, `half_life`, owner pointer, local `rank`, `persist_interval`, cached encoded buffer, and `CephContext`. `ConnectionReport` stores rank, current liveness map, historical score map, report epoch, and epoch version. Persistence is external: the tracker only encodes itself and asks its `RankProvider` owner to write it.

## Dependencies and integration points
The file depends on Ceph encoding, formatter, debug logging, `RankProvider`, and monitor election code. `Elector` owns a `ConnectionTracker`, persists it in the monitor store, sends encoded reports in election and ping messages, and queries netsplit pairs for health/reporting.

## Risks and edge cases
Negative or self ranks are dropped or logged, but rank-removal rewriting is complex and depends on ordered maps. `get_total_connection_score()` assumes `current` contains entries matching `history`; missing `current` entries would dereference an invalid iterator. Netsplit detection mutates `peer_reports[rank]` inside a query. Score aging uses caller-supplied time units and assumes they are bounded by real elapsed time. Persist interval zero would be unsafe, so configuration must avoid it.

## Test signals
Tests should cover live/dead score movement and clamping, peer report freshness rules, encode/decode round trips, cached encoding invalidation, persist callback frequency, rank change/removal map rewriting, clean tracker checks, netsplit detection with down monitors, and malformed/missing current/history pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConnectionTracker.cc -->
