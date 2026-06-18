# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEnabledECPolicies.java

## Purpose
`TestEnabledECPolicies` validates how `ErasureCodingPolicyManager` initializes and reports enabled erasure-coding policies from configuration, including invalid policy names, default policy changes, and persisted-vs-effective policy state.

## Important APIs, Types, And Functions
The test uses `HdfsConfiguration`, `DFS_NAMENODE_EC_SYSTEM_DEFAULT_POLICY`, `ErasureCodingPolicyManager`, `SystemErasureCodingPolicies`, `ErasureCodingPolicy`, `ErasureCodingPolicyInfo`, and `ErasureCodingPolicyState`. Helpers `expectInvalidPolicy`, `expectValidPolicy`, `testGetPolicies`, `constructAllDisabledInitialPolicies`, `isPolicyEnabled`, and `assertAllPoliciesAreDisabled` isolate manager behaviors.

## Control Flow
`testDefaultPolicy` reads the configured default policy and expects one enabled policy. `testInvalid` feeds malformed policy lists and expects initialization failures. `testValid` enables the default striped policy. `testGetPolicies` enables zero, one, and two policies, then checks uniqueness and `getEnabledPolicyByName` filtering. `testChangeDefaultPolicy` changes the configured default, simulates fsimage loading with all persisted policies disabled, and verifies how effective enabled state differs from persisted state until explicit disable/enable operations occur.

## State And Persistence Behavior
The distinction between effective runtime policy state and persisted policy state is the central persistence concern. A newly configured default policy can be effectively enabled after init/load even when it remains disabled in the persisted list until an explicit enable operation. Setting the default to an empty string should leave all policies disabled after loading.

## Dependencies And Integration Points
The manager is a singleton, so tests repeatedly call `init` to reset state. The file integrates configuration defaults, system policy definitions, and fsimage-like `loadPolicies` input. It does not start a cluster; it tests policy manager logic directly.

## Risks And Test Signals
Risks include accepting invalid policy names, duplicate enabled-policy results, exposing disabled policies through enabled lookups, and persisting default-policy state incorrectly. Test signals are exception messages, enabled-policy counts, uniqueness checks, null/non-null lookup results, and state comparisons across `getPolicies` and `getPersistedPolicies`.
