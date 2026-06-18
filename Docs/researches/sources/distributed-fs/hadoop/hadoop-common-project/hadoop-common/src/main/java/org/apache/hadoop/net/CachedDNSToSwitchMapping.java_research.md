<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/CachedDNSToSwitchMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/CachedDNSToSwitchMapping.java

## Purpose
`CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping` and caches normalized host or IP to rack/network-location results.

## Important APIs and Types
The class extends `AbstractDNSToSwitchMapping`. Important APIs are constructor, `resolve`, `getSwitchMap`, `isSingleSwitch`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String>)`. It uses a `ConcurrentHashMap` for cache storage.

## Control Flow
`resolve` normalizes all input names with `NetUtils.normalizeHostNames`, returns empty for empty input, identifies uncached hosts, resolves only those through the raw mapping, caches non-null results, then returns the full list from cache. If the raw mapping returns null for uncached hosts, the final lookup returns null if any requested host remains missing.

## State and Persistence
State is the in-memory cache. Reload methods clear all or selected host entries. The raw mapping is final and not owned by this class.

## Dependencies and Integration Points
This wrapper is commonly used by Hadoop network topology code to avoid repeated external script or DNS lookups. Single-switch behavior delegates to the raw mapping via `AbstractDNSToSwitchMapping.isMappingSingleSwitch`.

## Risks and Test Signals
Selective reload removes the exact supplied names without normalization, while `resolve` stores normalized names, so callers passing hostnames may fail to evict normalized IP keys. Tests should cover normalization, null raw results, partial cache hits, cache snapshots, clear/reload behavior, and raw mapping call counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/CachedDNSToSwitchMapping.java -->
