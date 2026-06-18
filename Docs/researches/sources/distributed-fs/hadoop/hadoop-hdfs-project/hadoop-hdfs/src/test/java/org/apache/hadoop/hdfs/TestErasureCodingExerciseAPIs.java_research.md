# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingExerciseAPIs.java

## Purpose
Exercises broad `FileSystem` and `HdfsAdmin` APIs with erasure coding enabled at the root. The test asserts that ordinary namespace, security, metadata, cache, snapshot, storage-policy, encryption-zone, and file APIs still work for EC directories/files, while EC-unsupported append and truncate fail.

## Important APIs and Types
APIs include ACL methods, xattrs, quotas, cache pools/directives, snapshots, symlinks, file create/open/concat/checksum/rename/delete, storage policies, EC policy add/disable/remove/set/unset, encryption-zone creation/reencryption, and delegation tokens. Important types include `AclEntry`, `AclStatus`, `CachePoolInfo`, `CacheDirectiveInfo`, `SnapshotDiffReport`, `FileEncryptionInfo`, `LocatedBlocks`, `BlockStoragePolicySuite`, `ECSchema`, and `Credentials`.

## Control Flow
`setupCluster()` enables ACLs, configures a JKS key provider, starts enough DataNodes for the default EC policy, enables all EC policies, and sets the root EC policy. Tests then independently validate access/owner/time metadata, quota summaries, cache operations, EC policy lifecycle, ACL mutation, xattr CRUD, snapshot lifecycle and diff report, symlink status, file operations including concat and checksum stability across rename, encryption-zone file metadata and reencrypt start, storage-policy set/unset, and expected failures for append/truncate.

## State, Persistence, Dependencies, Integration
State spans root-inherited EC policy, per-file EC layout, ACL and xattr metadata, snapshots, cache manager state, key-provider state, encryption-zone EDEKs, delegation credentials, and storage policy metadata. Dependencies include MiniDFSCluster, JKS provider setup, ACL enablement, all system EC policies, and helper wrappers.

## Risks and Test Signals
Signals are successful completion of many public APIs under EC plus explicit append/truncate exceptions. Risks include broad tests masking exact failure sources and some assertions checking no-op semantics, but the suite is valuable as a regression net for cross-feature EC compatibility.
