# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CombinedIPList.java

Purpose: `CombinedIPList` combines fixed and optional cache-refreshable variable IP/subnet blacklist files behind one `IPList`.

Important APIs and types: constructor accepts fixed file path, variable file path, and cache expiry seconds. `isIn(String)` checks membership across the configured lists.

Control flow: construction always creates a `FileBasedIPList` for the fixed file. If a variable file is supplied, it wraps another `FileBasedIPList` in `CacheableIPList`. `isIn` rejects null input, then returns true on the first list that contains the address.

State and persistence behavior: stores an array of IP list delegates. It reads list files through delegates and may reload variable lists; no writes.

Dependencies and integration points: used by access-control or network filtering components; depends on `FileBasedIPList`, `CacheableIPList`, and `IPList`.

Risks: null fixed file behavior depends on `FileBasedIPList`. Cache expiry parameter name says seconds but `CacheableIPList` treats it as a raw millisecond timeout, so callers must align units. Null IP input throws.

Test signals: cover fixed-only membership, fixed plus variable membership, null variable file, null input failure, cache refresh, and first-match behavior.
