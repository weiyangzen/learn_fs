# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AddErasureCodingPolicyResponse.java

## Purpose
`AddErasureCodingPolicyResponse` represents the per-policy result of adding an erasure coding policy.

## Important APIs, types, and functions
Constructors create success responses from an `ErasureCodingPolicy` or failure responses from an error string or `HadoopIllegalArgumentException`. Getters expose success, policy, and error message. `toString`, `equals`, and `hashCode` include policy, success flag, and error message.

## Control flow
Construction sets `succeed` based on constructor choice. `toString` branches between success and failure text.

## State and persistence behavior
State is the policy reference, boolean success flag, and optional error string. No local persistence occurs; objects are protocol values.

## Dependencies and integration points
It depends on `ErasureCodingPolicy`, `HadoopIllegalArgumentException`, and Apache Commons builders. It is used by erasure coding admin APIs and RPC responses.

## Risks and test signals
Tests should cover success/failure constructors, null or present error messages, equality/hash consistency, and string output. A failure response still carries a policy, so callers should not infer null policy on failure.
