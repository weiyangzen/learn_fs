# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicies.java

## Purpose
Tests the main HDFS erasure-coding policy contract: inheritance, file-level override, replicated override, listing/status reporting, permission checks, user-defined policy validation, policy-manager limits, reserved raw paths, persistence through restarts, and coexistence of multiple system policies.

## Important APIs and Types
Important APIs include `setErasureCodingPolicy`, `unsetErasureCodingPolicy`, `getErasureCodingPolicy`, `getAllErasureCodingPolicies`, `addErasureCodingPolicies`, `getAllErasureCodingCodecs`, `createFile().ecPolicyName(...)`, `createFile().replicate()`, `DFSClient.create`, `setReplication`, and `listPaths`. Types include `ErasureCodingPolicy`, `ErasureCodingPolicyInfo`, `SystemErasureCodingPolicies`, `ErasureCodingPolicyManager`, `ECSchema`, `HdfsFileStatus`, `INodeFile`, `ContentSummary`, and `AccessControlException`.

## Control Flow
The setup starts enough DataNodes for the selected policy and enables all EC policies. Tests then cover replicated files already under a directory later marked EC, content summary inheritance, basic set-policy behavior and restart/fsimage loading, legal moves between EC and non-EC directories, setReplication no-op behavior on EC files, reserved `/.reserved/raw` policy mapping, invalid/default policy setting, listing all policies/codecs, missing-path failures, multiple policy coexistence, permission enforcement for normal users versus superuser, file-level EC policy override, explicit replicated file creation under EC parents, invalid user-defined policies, maximum user-defined policy IDs, replication policy hiding, and different cell-size policies.

## State, Persistence, Dependencies, Integration
State includes EC policy xattrs/IDs on directories and files, INode striped flags, policy-manager registry entries, user-defined policy IDs, permissions, fsimage/edit-log records, and content summary metadata. Integration spans public `DistributedFileSystem`, lower-level `DFSClient`, `HdfsAdmin`, NameNode `FSNamesystem`/INode inspection, and user impersonation.

## Risks and Test Signals
Signals include exact policy equality on files/directories/listings, null policy for replicated overrides, exceptions for invalid policies and missing paths, access-denied behavior, ID exhaustion failure, and policy retention after NameNode restart. Risks include broad stateful coverage and some swallowed exception patterns, but it is the central regression suite for EC policy semantics.
