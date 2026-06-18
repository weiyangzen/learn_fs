# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLease.java

## Purpose
Tests HDFS client lease lifecycle, lease-renewal failure handling, lease movement across renames, file recreation after rename, delete/open-file validation, and `LeaseRenewer` sharing per user.

## APIs and Control Flow
`hasLease` and `leaseCount` inspect Namenode lease state through `NameNodeAdapter`. `testLeaseAbort` uses a spied `NamenodeProtocols` to make `renewLease` throw `InvalidToken`, simulates soft and hard renewal expiry, verifies writes continue past soft failure but fail after hard failure, confirms the renewer empties, then verifies reads and new writes still work. `testLeaseAfterRename` opens a file, renames it through several directory cases, and checks the lease follows the destination. `testLeaseAfterRenameAndRecreate` verifies inode IDs allow a renamed open file and a newly created file at the old path to coexist. `testLease` checks leases for open files and that flushing after deleting the parent fails. `testFactory` uses a mocked `ClientProtocol` to verify `DFSClient` instances for the same UGI share a renewer while different UGIs do not.

## State, Dependencies, Integration
State includes Namenode lease tables, client renewer timestamps, open streams, rename metadata, and mocked protocol responses. Dependencies include `LeaseRenewer`, `NameNodeAdapter`, `Mockito`, `UserGroupInformation`, `DFSClient`, and `NamenodeProtocols`. It integrates client lease management with namespace mutations and user identity.

## Risks and Test Signals
Signals are lease counts, path-specific lease existence, expected IO failures, renewer identity, and content checks. Risks include internal timestamp mutation (`dfs.lastLeaseRenewal`), sleep-based renewer cleanup, mocked protocol drift, and brittle exception behavior after deleted parent paths.
