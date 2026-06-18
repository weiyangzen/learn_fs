# sources/distributed-fs/ceph/src/mon/KVMonitor.h

## Purpose
`KVMonitor.h` declares the Paxos-backed monitor config-key service and helper API for OSD private key material.

## Important APIs, Types, and Members
`KVMonitor` derives from `PaxosService`, stores `version`, and keeps pending key updates as `map<string, optional<bufferlist>>`. Public methods cover Paxos lifecycle, command preprocess/prepare, OSD new/destroy validation and mutation, subscriptions, and external `enqueue_set()`/`enqueue_rm()`.

## Control Flow
Monitor command dispatch splits reads and writes between preprocess and prepare methods. External callers may enqueue KV changes but must also force proposal/commit to preserve atomicity and subscriber notification.

## State and Persistence
The header registers both the service prefix and `KV_PREFIX` through `get_store_prefixes()`; implementation persists versioned deltas and current key values.

## Dependencies and Integration Points
It depends on `PaxosService`, `MonSession`, `Subscription`, `uuid_d`, and `bufferlist`.

## Risks
External enqueue helpers are low-level and easy to misuse without a matching proposal. Prefix scans may become expensive on large stores.

## Test Signals
Verify lifecycle, store prefix registration, enqueue semantics, OSD helper contracts, and subscription update behavior.
