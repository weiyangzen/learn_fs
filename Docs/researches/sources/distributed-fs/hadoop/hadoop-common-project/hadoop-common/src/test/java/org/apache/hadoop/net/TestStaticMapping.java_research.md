# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestStaticMapping.java

## Purpose
Tests `StaticMapping` and its interaction with `CachedDNSToSwitchMapping`, including static map reset, config-loaded mappings, single/multi-switch policy, positive and negative cache entries.

## Important APIs, Types, And Functions
Uses `StaticMapping.resetMap()`, `addNodeToRack()`, `resolve()`, `getSwitchMap()`, `dumpTopology()`, `setConf()`, `CachedDNSToSwitchMapping`, and `AbstractDNSToSwitchMapping.isMappingSingleSwitch()`.

## Control Flow
Helper `newInstance()` resets static state before creating mappings. Tests assert single-switch with no script and multi-switch with a script, add a node and resolve known/unknown hosts, parse config `n1=/r1,n2=/r2`, and verify cached mappings relay single-switch/multi-switch queries and fill cache after resolve.

## State And Persistence Behavior
The underlying mapping is static JVM state and is reset by helpers. Cached mapping has its own cache, which can include negative/default-rack entries for unknown hosts.

## Dependencies And Integration Points
Validates test mapping behavior used by mini clusters and topology-aware tests, plus the caching wrapper used in production-style resolution paths.

## Risks
Static map leakage is the largest risk. Single-switch status is driven by script config, not rack entries, which can surprise callers. Negative caching stores unknown hosts, so later additions may not be visible through an existing cache without reload.

## Test Signals
Signals include `/r1` for `n1`, default rack for unknown, switch map sizes 0/1/2 as cache fills, and correct delegation of single/multi-switch status through cache wrappers.
