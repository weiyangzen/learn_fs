# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CombinedIPWhiteList.java

Purpose: `CombinedIPWhiteList` combines fixed and optional variable whitelist files, always allowing localhost.

Important APIs and types: constructor mirrors `CombinedIPList`; `isIn(String)` checks whitelist membership and treats `127.0.0.1` specially.

Control flow: it builds fixed and optional cacheable variable delegates. `isIn` rejects null input, returns true for localhost, then tests each delegate until one contains the address.

State and persistence behavior: stores delegate IP lists and reads/reloads files through them. No writes.

Dependencies and integration points: used by network allow-list checks; depends on `FileBasedIPList`, `CacheableIPList`, and `IPList`.

Risks: localhost bypass is unconditional and only covers IPv4 loopback string, not `::1`. Cache expiry unit naming has the same risk as `CombinedIPList`. Null input throws.

Test signals: cover localhost acceptance, fixed/variable matches, nonmatches, null input failure, null variable file, and cache refresh behavior.
