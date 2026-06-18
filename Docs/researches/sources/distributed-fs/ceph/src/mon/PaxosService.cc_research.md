# sources/distributed-fs/ceph/src/mon/PaxosService.cc

## Purpose
`PaxosService.cc` implements the common monitor-service orchestration around Paxos. It gates client/service messages on readable and writeable Paxos state, batches service-specific pending updates into the shared Paxos transaction, refreshes cached versions from the monitor store, trims old service versions, and persists service health checks.

## Important APIs, Types, and Control Flow
`dispatch()` is the main control flow: reject shutdown/stale election messages, ignore disconnected clients, wait for readability, run `preprocess_query()`, forward writes to the leader, wait for writeability, call `prepare_update()`, then immediately or eventually call `propose_pending()`. `should_propose()` dampens proposal frequency after startup. `propose_pending()` obtains `paxos.get_pending_transaction()`, optionally stashes a full copy, calls service `encode_pending()`, writes `format_version`, queues a `C_Committed` finisher, and triggers Paxos. `_active()` waits for Paxos active state, creates pending leader state, creates initial state when needed, wakes proposal waiters, runs format upgrades, and calls `on_active()`.

## State and Persistence Behavior
Cached `first_committed` and `last_committed` are refreshed from the service prefix. Versions are stored under the service name, full snapshots under `full/<version>`, and latest full snapshot under `full/latest`. `maybe_trim()` decides whether enough old versions can be removed, encodes trim operations, updates `first_committed`, lets services append extra trim metadata, and triggers a Paxos proposal. Health checks are encoded under the global `health` prefix keyed by `service_name`.

## Dependencies and Integration Points
This file integrates with `Monitor`, `Paxos`, `PaxosServiceMessage`, monitor timers, config knobs such as Paxos proposal and trim intervals, `MonitorDBStore`, health logging, and operation retry contexts. Service subclasses provide all domain-specific state transitions through virtual hooks declared in the header.

## Risks and Test Signals
Risks include callback ordering around proposals, stale forwarded requests, delayed proposal timers firing after elections, trimming too aggressively, and read waits that must choose between service-level and Paxos-level wait queues. Tests should cover read-only preprocessing, leader forwarding, delayed and forced proposals, election restart cancellation, initial state proposal, health persistence, format upgrades, and trim min/max behavior.
