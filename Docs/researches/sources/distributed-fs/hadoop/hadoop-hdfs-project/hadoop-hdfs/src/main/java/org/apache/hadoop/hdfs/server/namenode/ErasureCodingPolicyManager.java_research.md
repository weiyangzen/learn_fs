# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ErasureCodingPolicyManager.java

## Purpose
`ErasureCodingPolicyManager` manages system and user-defined erasure coding policies for the NameNode. It tracks all known policies, enabled policies, removed policies, and the subset of policy state persisted into fsimage.

## Important APIs and Types
It is a lazy singleton returned by `getInstance`. State includes maps by name and ID, cached arrays of all/enabled policies, persisted policy info, maximum cell size, user-defined-policy enablement, and default policy name. Important APIs are `init`, `getEnabledPolicies`, `getEnabledPolicyByName`, `checkStoragePolicySuitableForECStripedMode`, `getPolicies`, `getPersistedPolicies`, `getCopyOfEnabledPolicies`, lookup by ID/name, `addPolicy`, `removePolicy`, `getRemovedPolicies`, `disablePolicy`, `enablePolicy`, `loadPolicies`, and `getEnabledPoliciesMetric`.

## Control Flow
Initialization loads built-in system policies as disabled, enables the configured default policy, caches arrays, then reads max cell size and user-defined enablement. Adding a policy validates user policy enablement, codec support, maximum block group size, maximum cell size, duplicate schema/cell-size/name, and ID exhaustion, then assigns a composed name and next user ID. Enable/disable/remove update both runtime enabled maps and persisted-policy state.

## State and Persistence
Runtime maps include built-in, user-defined, disabled, enabled, and removed policies. `allPersistedPolicies` captures the fsimage representation, intentionally treating a default policy enabled only by startup config differently from an explicitly enabled persisted policy.

## Dependencies and Integration
It integrates with `FSNamesystem`, inode EC policy xattrs, `SystemErasureCodingPolicies`, `ErasureCodingPolicyInfo`, `CodecUtil`, DFS config keys, and storage policy validation for striped files.

## Risks and Test Signals
The singleton lazy initialization is not synchronized, so concurrent early access could race. `init` calls `enableDefaultPolicy` before reading configured `maxCellSize`, so persisted loading later performs max-size checks with the initialized value but built-ins/defaults are handled earlier. `clear` is a placeholder. Tests should cover duplicate policy detection, ID assignment boundaries, disabled user-defined policies, unsupported codecs, persisted state differences for default policy, remove/disable/enable transitions, replication policy lookup, and storage-policy suitability.
