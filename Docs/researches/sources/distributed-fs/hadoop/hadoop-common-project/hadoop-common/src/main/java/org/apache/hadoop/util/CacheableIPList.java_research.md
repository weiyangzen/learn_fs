# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CacheableIPList.java

Purpose: `CacheableIPList` wraps a `FileBasedIPList` and reloads it on demand when a cache timeout expires or refresh is requested.

Important APIs and types: constructor accepts the file-backed list and timeout. `refresh()` forces expiration. `isIn(String)` checks membership and reloads if needed.

Control flow: cache expiry timestamp is volatile. `isIn` uses double-checked locking: if expiry is non-negative and in the past, it synchronizes and reloads via `ipList.reload()`, then delegates membership to the current list.

State and persistence behavior: stores timeout, volatile expiry time, and volatile current `FileBasedIPList`. Negative timeout disables automatic expiry. No writes to the backing file occur.

Dependencies and integration points: implements `IPList`; used by `CombinedIPList` and `CombinedIPWhiteList` for variable blacklist/whitelist files.

Risks: `refresh()` only sets expiry to zero; the next `isIn` performs reload. Reload failures depend on `FileBasedIPList.reload` behavior. System clock changes affect expiry.

Test signals: cover negative timeout no-reload, positive timeout reload, manual refresh, concurrent reload single execution, and membership delegation after file changes.
