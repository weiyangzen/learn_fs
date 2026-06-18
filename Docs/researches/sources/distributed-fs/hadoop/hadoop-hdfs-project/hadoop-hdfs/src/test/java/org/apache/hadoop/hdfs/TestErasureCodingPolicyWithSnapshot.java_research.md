# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicyWithSnapshot.java

## Purpose
Tests interactions between erasure-coding policy metadata and HDFS snapshots. It verifies snapshots preserve the policy state visible at snapshot time, copied snapshots do not preserve EC policy metadata, and EC `FileStatus` flags survive NameNode restart.

## Important APIs and Types
Uses `allowSnapshot`, `createSnapshot`, `deleteSnapshot`, `getErasureCodingPolicy`, `setErasureCodingPolicy`, `unsetErasureCodingPolicy`, safe mode/saveNamespace/restart, `FsShell -cp -px`, `ContractTestUtils.assertErasureCoded`, and `SystemErasureCodingPolicies`.

## Control Flow
Setup starts a cluster with `data + parity` DataNodes and enables the selected EC policy. Tests snapshot a parent directory containing an EC directory, delete/recreate the directory, take additional snapshots, and verify each snapshot path reports the historical policy or null. Other tests snapshot the EC directory itself, restart the NameNode after saving namespace, copy a snapshot and assert the copy lacks EC policy, compare normal and EC `FileStatus` before/after restart, verify `.snapshot` itself returns null rather than throwing, and create snapshots across policy changes from null to RS-6-3 to unset to RS-3-2.

## State, Persistence, Dependencies, Integration
State includes snapshot inode references, EC policy xattrs/IDs, file contents, fsimage persistence, and file status flags. Integration points are snapshot manager, EC policy manager, FsShell copy semantics, NameNode restart, and contract-test utilities.

## Risks and Test Signals
Signals are precise policy equality/nullness on snapshot paths, content preservation, copied snapshot policy absence, and restart-stable `isErasureCoded` status. Risks are path construction around snapshot names and assumptions about copy behavior, but these are exactly the client-visible contracts under test.
