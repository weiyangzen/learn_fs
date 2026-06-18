# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicyInfo.java

## Purpose
`ErasureCodingPolicyInfo` wraps an `ErasureCodingPolicy` with its mutable lifecycle state: disabled, enabled, or removed.

## APIs and Behavior
The primary constructor requires non-null policy and state; the convenience constructor defaults to `DISABLED`. `getPolicy()`, `getState()`, `setState()`, and boolean predicates expose and mutate state. Equality, hash code, and `toString()` include both policy and state.

## State, Dependencies, and Integration
The policy reference is final, but state is mutable. It is serializable and consumed by `ClientProtocol.getErasureCodingPolicies`, policy enable/disable/remove operations, and admin display code.

## Risks and Test Signals
Mutable state inside an otherwise value-like wrapper can surprise caches. Tests should cover null rejection, default disabled state, state transitions, equality changes after mutation, and RPC conversion for removed policies that may still be referenced by existing files.
