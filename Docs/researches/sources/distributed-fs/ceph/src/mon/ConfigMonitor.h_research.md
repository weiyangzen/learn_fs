<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMonitor.h -->
# sources/distributed-fs/ceph/src/mon/ConfigMonitor.h

## Purpose
`ConfigMonitor.h` declares the monitor Paxos service responsible for cluster configuration state. It exposes loading, command handling, config delivery, subscription checks, and Paxos lifecycle hooks.

## Important APIs, types, and functions
`ConfigMonitor` derives from `PaxosService`. Its state fields are `version`, `ConfigMap config_map`, `pending`, `pending_description`, `pending_cleanup`, and `current`. `pending` and `pending_cleanup` map string keys to optional bufferlists, where an empty optional means removal. Public APIs include `load_config()`, `load_changeset()`, command preprocess/prepare methods, `handle_get_config()`, Paxos hooks, `refresh_config()`, `maybe_send_config()`, `send_config()`, and subscription helpers.

## Control flow
The header establishes a two-lane flow: read-only commands and config fetches can be answered from the loaded `config_map`, while mutating commands are prepared, encoded to KVMonitor, and then committed through Paxos. Subscriptions are checked after version advances or when sessions request config updates.

## State and persistence behavior
The declaration shows that `ConfigMonitor` keeps in-memory current/pending maps, not the durable key/value store itself. Persistence is implemented by `encode_pending_to_kvmon()` and `encode_pending()` in the `.cc` file; `encode_full()` is intentionally empty because this service's real data is in KVMonitor.

## Dependencies and integration points
The header depends on `ConfigMap`, `PaxosService`, Ceph bufferlists, monitor sessions, and subscriptions. It is used by `Monitor` to route config commands, daemon config requests, auth completion subscription checks, and periodic service ticks.

## Risks and edge cases
Because the private `encode_pending_to_kvmon()` is separate from `encode_pending()`, callers preparing mutations must remember to enqueue KV changes before proposing ConfigMonitor state. Any future full-state behavior must account for the empty `encode_full()` override.

## Test signals
Compile coverage should confirm the service satisfies `PaxosService` overrides. Runtime tests should validate pending optional semantics, subscription update behavior, and empty full-encode behavior during monitor sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMonitor.h -->
