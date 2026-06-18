# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/Groups.java


Purpose: `Groups` is Hadoop's central user-to-groups service. It wraps a configured `GroupMappingServiceProvider` with positive caching, optional negative caching, static overrides, metrics, and singleton access.

Important APIs and types: Constructors accept `Configuration` and optional `Timer`. Public APIs include deprecated list-returning `getGroups()`, preferred `getGroupsSet()`, background refresh counters, `refresh()`, `cacheGroupsAdd()`, singleton getters, loaded-configuration reset, and test reset. The inner `GroupCacheLoader` owns Guava cache load/reload behavior.

Control flow: Construction instantiates the configured provider, reads cache timeouts, warning thresholds, background reload settings, parses static overrides, builds a Guava `LoadingCache`, and optionally builds a negative cache. Lookup first checks static mapping, then negative cache, then `cache.get(user)`. Cache load traces and calls `impl.getGroupsSet(user)`, records metrics, warns on slow lookups, stores non-empty groups, and throws for empty groups to avoid positive caching of misses. Reload is synchronous unless background reload is enabled, in which case old values are returned while a daemon executor refreshes.

State and persistence: State is in-memory only: cache entries, negative cache entries, static override map, counters, and singleton instance. Static overrides are loaded from configuration and not persisted by the class. `refresh()` invalidates positive and negative caches and asks the provider to refresh its own state.

Dependencies and integration: It depends on Guava cache/listenable futures, Hadoop `Timer`, `Configuration`, `ReflectionUtils`, tracing, `UserGroupInformation.metrics`, and mapping providers such as JNI or shell fallback. Permission checks and UGI rely on this service for group membership.

Risks and test signals: Tests should cover static overrides, negative-cache expiration, no-groups exceptions, background reload counters, singleton reset, cache invalidation, and warning metrics. Operational risks include stale groups until refresh/expiry, thread-pool pressure during background reload, and treating empty provider results as hard user misses.
