# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/StaticMapping.java

## Purpose
Static in-memory `DNSToSwitchMapping` implementation for tests and mini-cluster simulations needing deterministic host-to-rack mappings.

## Important APIs, Types, And Functions
Extends `AbstractDNSToSwitchMapping`. Provides config key `hadoop.configured.node.mapping`, `setConf()`, compatibility `setconf()`, static `addNodeToRack()`, `resolve()`, `isSingleSwitch()`, `getSwitchMap()`, `resetMap()`, and no-op reload methods.

## Control Flow
`setConf()` parses comma-delimited `host=rack` strings from configuration and adds them to the static map. `resolve()` synchronizes on the map and returns a rack for each input or `NetworkTopology.DEFAULT_RACK`. `isSingleSwitch()` delegates to script-policy logic rather than map contents.

## State And Persistence Behavior
The host-to-rack map is static JVM-wide and persists across instances until `resetMap()` is called. Configuration-loaded entries are not removed when an instance is discarded.

## Dependencies And Integration Points
Integrates with `AbstractDNSToSwitchMapping`, `ScriptBasedMapping` policy semantics, `Configuration`, and `NetworkTopology`.

## Risks
Static state can leak between tests unless reset. Config parsing assumes every mapping contains `=` and preserves spaces as significant. Single-switch reporting depends on topology script configuration, not whether multiple racks are present.

## Test Signals
Expected signals include known hosts resolving to configured racks, unknown hosts resolving to `/default-rack`, `getSwitchMap()` returning a defensive copy, and reload methods not changing state.
