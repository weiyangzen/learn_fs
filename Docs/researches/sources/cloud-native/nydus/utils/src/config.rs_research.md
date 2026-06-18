# sources/cloud-native/nydus/utils/src/config.rs

Purpose: global scoped configuration store for runtime string settings such as registry auth, proxy URL, and Dragonfly scheduler endpoint.

Important APIs/types/functions: `CONFIG_MAP` is `ArcSwap<HashMap<String, String>>`. `Keys` enumerates `RegistryAuth`, `ProxyURL`, and `DragonflySchedulerEndpoint`, with conversions to/from strings. Public functions include `set`, `set_if_empty`, `get_changed`, `get`, `remove`, `clear`, `contains_key`, `keys`, `len`, `is_empty`, and `get_all`.

Control flow: keys are stored as `"id:key"` strings. Writers clone the current map, mutate the clone, and atomically store a new `Arc<HashMap<...>>`. Readers load the current map snapshot and clone values as needed. `set_if_empty` reads the current value and only writes a non-empty replacement if the current value is empty. `get_all(Some(id))` strips the `id:` prefix and returns only entries for that id; `None` clones the whole map.

State and persistence: all configuration is process-global and in-memory. There is no persistence across process restart.

Dependencies and integration points: uses `arc-swap` for lock-free read-mostly access and `lazy_static`. Likely used by backend/auth/proxy code to update live configuration for mounted instances.

Risks: concurrent writers can lose updates because each write clones from a snapshot and replaces the entire map without compare-and-swap retry. `set_if_empty` is not atomic relative to other writers. Empty string values are indistinguishable from missing values for `get`, though `contains_key` can distinguish them. Plain `"id:key"` concatenation can collide if ids contain chosen key suffix patterns, though current filtering uses exact prefix.

Test signals: many tests cover set/get, missing keys, change detection, removal, clearing, key listing, length, update, special characters, large values, filtered `get_all`, `set_if_empty`, and key conversion. Tests serialize access with a global lock; the "concurrent" test joins threads sequentially and does not expose lost-update races.
