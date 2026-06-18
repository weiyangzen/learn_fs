# sources/distributed-fs/ceph/src/mon/PaxosService.h

## Purpose
`PaxosService.h` declares the abstract base class for monitor services replicated through Paxos. It standardizes message dispatch, pending-state lifecycle, store key conventions, version caches, health-check persistence, read/write wait behavior, trimming, and full-state stashing.

## Important APIs, Types, and Control Flow
`PaxosService` stores references to `Monitor` and `Paxos`, the service name, proposal flags, `service_version`, `format_version`, and pending/proposal timers. Subclasses must implement `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `preprocess_query()`, `prepare_update()`, and `encode_full()`. Optional hooks include `post_paxos_update()`, `init()`, `discard_pending()`, `on_active()`, `upgrade_format()`, `on_upgrade()`, `on_restart()`, `tick()`, `get_trim_to()`, and `encode_trim_extra()`. Callback helpers `C_RetryMessage` and `C_ReplyOp` integrate monitor op retry and reply completion.

## State and Persistence Behavior
The class owns version cache fields, `waiting_for_commit`, `waiting_for_finished_proposal`, and standard store key names: `last_committed`, `first_committed`, `full`, and `latest`. Store helpers write committed version values, full snapshots, integer values, and arbitrary bufferlists under the service prefix. `put_last_committed()` also initializes `first_committed` on the first proposal to satisfy service assumptions.

## Dependencies and Integration Points
It depends on Ceph contexts, `health_check.h`, `MonitorDBStore`, and `MonOpRequest`. The class is the bridge between domain monitors such as OSD, MDS, auth, config, and manager services and the shared `Paxos` instance.

## Risks and Test Signals
Risks include subclass contract violations, proposing without pending state, stale cached versions, format-version mismatch handling, and incorrect distinction between Paxos active/readable/writeable and service active/readable/writeable. Tests should use fake subclasses to validate initial-state creation, callback waits, full snapshot stashing, store-key writes, trim extras, health encoding, and dispatch retry behavior.
