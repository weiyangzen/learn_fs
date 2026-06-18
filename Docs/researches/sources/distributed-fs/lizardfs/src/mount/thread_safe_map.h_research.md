## sources/distributed-fs/lizardfs/src/mount/thread_safe_map.h

Purpose: generic mutex-protected unordered map with a monotonically increasing generated key.

Important APIs: `put(key, data)` stores/replaces data; `take(key)` removes and returns `{true, data}` or `{false, default}`; `generateKey()` increments and returns `next_key_`.

State and dependencies: owns a `std::unordered_map<K, D>`, `std::mutex`, and key counter initialized to zero.

Risks: `take` default-constructs `D` even on miss, so `D` must be default constructible. Key overflow and zero-as-special semantics are caller concerns. It does not expose lookup without removal.

Test signals: concurrent put/take/generateKey, missing keys, duplicate puts, and generated-key wrap behavior for small integral key types.
