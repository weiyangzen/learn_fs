# sources/control-plane/mayastor/io-engine/src/store/etcd.rs

## Purpose
This file implements the generic `Store` trait for etcd using the `etcd-client` crate.

## Important APIs, Types, And Functions
`Etcd(Client)` wraps an etcd client. `Etcd::new` connects to an endpoint. The `Store` implementation provides `put_kv`, `put_kv_cas`, `get_kv`, `delete_kv`, and `online`.

## Control Flow
`put_kv` serializes values to JSON bytes and writes them to etcd. `put_kv_cas` builds an etcd transaction comparing the current value with an expected byte vector; on success it writes the new value, and on compare failure it returns the current stored value if present. `get_kv` reads the first key-value pair and deserializes JSON. `delete_kv` deletes the key. `online` checks etcd status.

## State, Persistence, And Dependencies
Persistent state is etcd key-value data. The wrapper stores a client handle and is cloneable. Dependencies include `etcd_client`, `serde_json`, `async_trait`, SNAFU error contexts, and store trait definitions.

## Integration Points
`PersistentStore` uses this as its backing store. Higher layers pass keys and serializable values through the generic store traits.

## Risks
`put_kv` uses `serde_json::to_string(value).unwrap()` in error context after `to_vec` succeeded; this is probably safe for the same value but still a panic path. CAS compare is byte-for-byte JSON, so semantically equal values with different serialization cannot match. `get_kv` returns only the first KV and treats absence as `MissingEntry`.

## Test Signals
Test connection failure, JSON put/get round trip, missing key, delete, CAS success, CAS conflict returning current bytes, malformed stored JSON deserialization failure, and `online` false when etcd is unavailable.
