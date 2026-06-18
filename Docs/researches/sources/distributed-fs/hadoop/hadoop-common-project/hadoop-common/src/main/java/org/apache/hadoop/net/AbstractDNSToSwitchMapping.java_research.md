<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/AbstractDNSToSwitchMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/AbstractDNSToSwitchMapping.java

## Purpose
`AbstractDNSToSwitchMapping` is the recommended base class for pluggable host-to-rack mapping implementations. It provides configuration storage, default topology diagnostics, and a single-switch predicate.

## Important APIs and Types
It implements `DNSToSwitchMapping` and `Configurable`. APIs include constructors, `getConf`, `setConf`, `isSingleSwitch`, `getSwitchMap`, `dumpTopology`, `isSingleSwitchByScriptPolicy`, and static `isMappingSingleSwitch`.

## Control Flow
The base class does not implement `resolve`. `dumpTopology` obtains a diagnostic map, emits mapping implementation identity, each host-to-switch entry, and counts unique switches. `isSingleSwitchByScriptPolicy` checks whether no topology script is configured. The static helper returns true only when the mapping is an `AbstractDNSToSwitchMapping` that reports single switch.

## State and Persistence
State is a retained `Configuration` reference. There is no persistent data.

## Dependencies and Integration Points
Network topology and block placement code query this base to decide whether multi-rack policies apply. Subclasses can expose cache contents through `getSwitchMap`.

## Risks and Test Signals
The Javadoc says non-derived mappings are assumed multi-switch, and the helper implements that by returning false for non-derived mappings. Tests should cover config retention, diagnostics with null/non-null maps, unique switch counts, script-policy behavior, and static predicate behavior for null, non-derived, and derived mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/AbstractDNSToSwitchMapping.java -->
