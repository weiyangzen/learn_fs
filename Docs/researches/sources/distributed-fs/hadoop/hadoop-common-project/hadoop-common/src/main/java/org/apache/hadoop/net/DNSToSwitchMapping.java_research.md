<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMapping.java

## Purpose
`DNSToSwitchMapping` is the pluggable contract for resolving hostnames or IP addresses to network topology paths such as rack locations.

## Important APIs and Types
The interface declares `resolve(List<String> names)`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String> names)`.

## Control Flow
Implementations must maintain one-to-one correspondence between input hosts and returned network paths. Empty input should return an empty list. Implementations are encouraged to use `NetworkTopology.DEFAULT_RACK` when a name cannot be resolved.

## State and Persistence
State is implementation-defined. The reload methods imply that implementations may cache mappings and must provide a way to clear all or selected entries.

## Dependencies and Integration Points
HDFS and other Hadoop placement policies depend on this interface to map data nodes to racks or fault domains. `CachedDNSToSwitchMapping` and script-based mappings are common implementations.

## Risks and Test Signals
Returning a wrong-sized list can corrupt topology assumptions. Null results have special meanings in some wrappers. Tests for implementations should cover empty input, unresolved hosts, ordering, cache reload, and consistency with network topology path syntax.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMapping.java -->
