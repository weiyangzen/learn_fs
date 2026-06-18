# sources/distributed-fs/ceph/src/mon/LogMonitor.h

## Purpose
`LogMonitor.h` declares the monitor service for cluster log persistence, replay, subscriptions, and external logging destinations.

## Important APIs, Types, and Members
`LogMonitor` derives from `PaxosService` and `md_config_obs_t`. It stores pending logs, pending keys, `LogSummary`, `external_log_to`, channel file descriptors, a formatting buffer, rotation flag, and nested `log_channel_info` maps/clients.

## Control Flow
Paxos lifecycle methods persist entries and summaries. Message dispatch handles logs and commands. Config observer callbacks refresh channel destinations, and `reopen_logs()` lazily rotates file descriptors.

## State and Persistence
Pending entries are in memory; durable state is summary, per-entry keys, versioned incrementals, and external progress. Channel destination clients are runtime-only.

## Dependencies and Integration Points
It references `MLog`, `Subscription`, `Formatter`, config observers, `LogEntry`, Graylog, journald, and string-map config helpers.

## Risks
The class owns OS fds and external logging clients. String-map config is parsed at runtime, so invalid values must degrade safely.

## Test Signals
Verify observer registration/removal, tracked keys, channel meta expansion, rotation flag behavior, and subscription type parsing.
