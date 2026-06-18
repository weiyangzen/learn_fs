# sources/control-plane/mayastor/io-engine/src/persistent_store.rs

## Purpose
This file provides the global persistent-store facade used to keep Mayastor state in etcd across restarts. It hides the etcd client behind `PersistentStore`, centralizes endpoint/timeout/retry configuration, and routes all store work onto the primary reactor so store users do not directly couple to the tokio-backed etcd client.

## Important APIs, Types, And Functions
`PersistentStoreBuilder` configures default port, endpoint, timeout, and retry count. `PersistentStore::put`, `txn_create_execute`, `get`, and `delete` are the public async operations. `execute_store_op` submits a closure to `Reactor::spawn_at_primary` and waits for a oneshot result with timeout/retry handling. `connect_to_backing_store`, `reconnect`, `enabled`, `endpoint`, `timeout`, `retries`, and `to_json_byte_vec` support initialization and diagnostics.

## Control Flow
Calling `PersistentStoreBuilder::connect` initializes the `OnceCell` only when an endpoint was provided. Store operations clone the current etcd client under a `parking_lot::Mutex`, spawn the actual `Store` trait call on the primary reactor, and wait with `tokio::time::timeout`. On operation failure or timeout, retries are attempted; when the backing store reports offline, the facade reconnects before retrying.

## State, Persistence, And Dependencies
Process state is held in `PERSISTENT_STORE: OnceCell<Mutex<PersistentStore>>` with endpoint, timeout, retries, and an `Etcd` client. Persistent state lives in etcd as JSON-serialized values. Dependencies include `store::etcd::Etcd`, `Store` traits and errors, `serde_json`, futures oneshots, `snafu`, and the Mayastor reactor abstraction.

## Integration Points
Any subsystem needing durable metadata can call the static `PersistentStore` methods without owning the etcd client. CAS creation uses `txn_create_execute`, which passes explicit new/expected byte values to the store backend. The file is also part of startup configuration because no endpoint means persistence is disabled.

## Risks
All static methods panic if called when persistence was not initialized, except `enabled`. Endpoint parsing treats any colon as an existing port, which is ambiguous for raw IPv6 addresses. Errors during serialization in `to_json_byte_vec` panic. The global mutex protects client replacement but can serialize all operations. Timeout/retry behavior may repeat non-idempotent writes unless higher-level keys are designed idempotently.

## Test Signals
Tests should cover disabled store startup, endpoint default-port insertion, successful put/get/delete, missing key propagation, CAS success and conflict return values, reconnect after an offline client, operation timeout and retry exhaustion, and reactor scheduling from non-primary contexts.
