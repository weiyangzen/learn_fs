# sources/distributed-fs/ceph/src/mon/LogMonitor.cc

## Purpose
`LogMonitor.cc` implements cluster log collection, durable log history, external log fanout, `log`/`log last` commands, and log subscriptions.

## Important APIs, Types, and Functions
Key methods include `create_initial`, `update_from_paxos`, `encode_pending`, `encode_full`, `should_stash_full`, `preprocess_log`, `prepare_log`, `_updated_log`, command handlers, subscription helpers, `log_external`, `log_external_backlog`, and `update_log_channels`. `log_channel_info` owns per-channel destination config.

## Control Flow
Incoming `MLog` entries are deduplicated against committed and pending keys, staged in timestamp order, and acknowledged after commit. CLI `log` stages a new `LogEntry`; `log last` reads recent entries. `log-<level>` subscribers receive incrementals from requested versions.

## State and Persistence
Quincy+ stores entries under per-channel sequence keys and Paxos incrementals with payloads plus prune bounds; full `LogSummary` snapshots are periodic. Legacy paths keep pre-Quincy summary behavior. `external_log_to` records external fanout progress in monitor-store meta.

## Dependencies and Integration Points
It integrates with `LogEntry`, `LogSummary`, `MLog`, `MLogAck`, monitor store, subscriptions, config observers, syslog, Graylog, journald, file logging, and `mon_cluster_log_*` settings.

## Risks
External replay must avoid duplicate or skipped logs across quorum changes. Mixed-version encoding is delicate. Cached file descriptors must close on rotation/config change. `log last` across all channels merges bounded tails.

## Test Signals
Cover dedupe, ack seq, v1/v2 decode, pruning, full stashing, `log last` filters, subscriber trims, external backlog, rotation, and config parsing.
