# sources/control-plane/mayastor/io-engine/src/store/store_defs.rs

## Purpose
This file defines the generic key-value store trait and the error taxonomy used by persistent store backends.

## Important APIs, Types, And Functions
`StoreError` covers connect, put/get/delete/txn/watch, wait-channel cancellation, missing entries, string conversion, serialization/deserialization, and operation timeout. `StoreKey` and `StoreValue` are blanket marker traits for key and serializable value types. `Store` defines async `put_kv`, `put_kv_cas`, `get_kv`, `delete_kv`, and `online`.

## Control Flow
Backend implementations use SNAFU contexts to construct `StoreError` variants. `PersistentStore` receives these errors and wraps wait/timeout behavior around trait calls.

## State, Persistence, And Dependencies
This file stores no state. It depends on `async_trait`, `etcd_client::Error`, `serde_json`, futures oneshot cancellation, and SNAFU.

## Integration Points
`store/etcd.rs` implements this trait. `persistent_store.rs` uses the trait bounds to remain backend-agnostic.

## Risks
Error variants are etcd-client-specific even though the trait is generic, which couples alternate backends to etcd error types or requires broader refactoring. Blanket `StoreKey` accepts any `ToString + Debug`, so poorly designed key string formats are not prevented by the type system.

## Test Signals
Tests should verify error display strings, blanket trait usability with expected key/value types, CAS trait signature behavior, and backend implementations mapping each error context correctly.
