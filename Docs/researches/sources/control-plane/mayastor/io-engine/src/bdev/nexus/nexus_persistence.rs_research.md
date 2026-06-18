## sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_persistence.rs

### Purpose
`nexus_persistence.rs` persists nexus restart-safety metadata into `PersistentStore`, primarily child health, clean shutdown, and a control-plane-requested self-shutdown bit. It protects nexus consistency by freezing I/O resubmissions while durable state is being changed and by self-shutting down when persistence cannot be trusted.

### Important APIs, Types, And Functions
`PersistentNexusInfo` wraps the stored `NexusInfo` plus an optional externally supplied store key. `NexusInfo` is the serialized state: `clean_shutdown`, `do_self_shutdown`, and `children`. `ChildInfo` records child UUID and health. `PersistOp` drives mutations: create, add/remove child, update child health, conditional update, and shutdown. `Nexus::persist()` is the main API, with `save()` and `save_txn()` performing retrying store writes and compare-and-set transactions.

### Control Flow
`persist()` exits early when persistence is disabled, which supports tests without a configured store. Otherwise it locks `nexus_info`, freezes nexus I/O mode, mutates the in-memory `NexusInfo` according to the requested operation, and writes the result to the store. `Create` rebuilds children from current nexus children and rejects a single unhealthy child. `UpdateCond` first evaluates its predicate under the nexus info lock, clones the expected state, applies the mutation, and calls `save_txn()`; a compare failure updates `do_self_shutdown` from the current store value and returns an error that triggers self-shutdown. Non-transactional writes call `save()` and retry with one-second sleeps until retry count expires.

### State, Persistence, And Dependencies
The durable JSON value is written via `PersistentStore::put()` or `txn_create_execute()` under either the supplied key or the nexus UUID. In-memory mutation is protected by the async `nexus_info` lock; I/O is frozen during persistence to avoid resubmission storms while etcd is slow or unavailable. Dependencies include `NexusChild::uuid()`, `IoMode`, serde JSON conversion, etcd client errors, `StoreError`, and `mayastor_sleep`.

### Integration Points
This file is used by nexus create/destroy and child state transitions. The conditional transaction is designed for control-plane republish races where another nexus may have picked up a replica while this nexus is marking it unhealthy. `try_self_shutdown()` is the enforcement path when persistence cannot be completed safely.

### Risks
The code uses `expect()` and `unwrap()` when parsing child UUIDs or current transaction values, so malformed internal state or unexpected store data can panic. I/O is restored to normal on most returns, but any added early return in the locked/frozen region must preserve that invariant. Transaction failure intentionally shuts the nexus down, so false compare failures from encoding drift would be disruptive. PersistentStore retry count underflow would be risky if configured as zero.

### Test Signals
Useful coverage includes disabled-store create/update, create with single unhealthy child, add-child replacement by UUID, remove-child idempotency, update-only changed child, conditional predicate false restoring normal I/O, transaction compare failure setting `do_self_shutdown`, retry exhaustion, shutdown write failure not self-shutting down, and store-key versus UUID-key selection.
