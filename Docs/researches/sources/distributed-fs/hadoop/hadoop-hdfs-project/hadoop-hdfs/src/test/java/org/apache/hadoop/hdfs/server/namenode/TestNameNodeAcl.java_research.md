# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeAcl.java

## Purpose
NameNode-specific ACL integration test class that inherits the full ACL API test suite from `FSAclBaseTest` and starts an HDFS cluster for NameNode interaction coverage.

## Important APIs, Types, and Functions
- Extends `FSAclBaseTest`.
- `BeforeAll init` assigns a new `Configuration` to inherited `conf` and calls inherited `startCluster()`.

## Control Flow
- This class defines no test methods directly; inherited tests execute against the cluster initialized here.
- The inherited suite covers ACL modification APIs and interaction between `setPermission` and inodes with ACLs.

## State and Persistence Behavior
- Cluster and filesystem state are managed by `FSAclBaseTest`.
- ACL changes are expected to be applied to NameNode inode metadata through the normal filesystem API.

## Dependencies and Integration Points
- Integrates inherited ACL tests with NameNode-backed HDFS rather than another filesystem implementation.
- Depends on inherited lifecycle and cleanup behavior.

## Risks and Edge Cases
- Local file is small, so most behavior is implicit in the base class; changes to `FSAclBaseTest` alter this class's coverage.
- Static inherited configuration/cluster setup can affect test isolation if base class state changes.

## Test Signals
- Delegated but important signal that NameNode supports the standard ACL API contract and permission interactions.
