# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingAddConfig.java

## Purpose
Verifies the configuration gate controlling addition of user-defined erasure coding policies. It ensures `dfs.namenode.ec.userdefined.policy.allowed` blocks additions when false and permits them when true.

## Important APIs and Types
Uses `DFS_NAMENODE_EC_POLICIES_USERPOLICIES_ALLOWED_KEY`, `DistributedFileSystem.addErasureCodingPolicies`, `AddErasureCodingPolicyResponse`, `ErasureCodingPolicy`, and `ECSchema`.

## Control Flow
Each test creates a fresh `HdfsConfiguration`, sets the policy-allowance flag, starts a zero-DataNode MiniDFSCluster, constructs an RS(5,3) policy with a 1 MiB cell size, and calls `addErasureCodingPolicies`. The disabled case asserts `isSucceed() == false` and the precise error message. The enabled case asserts success and a null error.

## State, Persistence, Dependencies, Integration
No file data is written. The relevant state is NameNode EC policy manager configuration and in-memory policy addition response. The zero-DataNode cluster emphasizes that policy validation is a NameNode/admin-plane operation independent of block placement.

## Risks and Test Signals
Signals are exact response success/error fields. The disabled test is sensitive to error-message wording, but this is useful for client-visible contract stability.
