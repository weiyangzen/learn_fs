# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestSwitchMapping.java

## Purpose
Tests generic `DNSToSwitchMapping` single-switch detection and cached wrapper string delegation.

## Important APIs, Types, And Functions
Uses `AbstractDNSToSwitchMapping.isMappingSingleSwitch()`, `CachedDNSToSwitchMapping`, `ScriptBasedMapping`, and a private `StandaloneSwitchMapping implements DNSToSwitchMapping`.

## Control Flow
Standalone non-abstract mapping is treated as multi-switch. Cached wrapper around it also reports multi-switch. Script mapping tests check that `toString()` for both direct and cached mappings includes either the configured script name or `ScriptBasedMapping.NO_SCRIPT`. Null mapping is treated as not single-switch.

## State And Persistence Behavior
State is per mapping object and its configuration. No external persistence.

## Dependencies And Integration Points
Confirms wrapper behavior for arbitrary `DNSToSwitchMapping` implementations and diagnostics from cached mappings.

## Risks
The default for unknown mapping implementations is conservative multi-switch, which may reduce optimization opportunities but avoids unsafe single-rack assumptions. String assertions are tied to diagnostic text.

## Test Signals
Expected signals are `false` for standalone and null mapping single-switch checks, and cached `toString()` containing the inner script name or no-script marker.
