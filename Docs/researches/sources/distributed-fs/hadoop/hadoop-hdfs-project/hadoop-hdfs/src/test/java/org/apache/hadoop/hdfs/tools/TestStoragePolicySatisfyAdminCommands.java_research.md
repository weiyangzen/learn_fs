# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestStoragePolicySatisfyAdminCommands.java

## Purpose
`TestStoragePolicySatisfyAdminCommands` validates the `-satisfyStoragePolicy` admin command with an external Storage Policy Satisfier, both for raw HDFS paths and URI-qualified paths.

## Important APIs, Types, And Functions
It uses `StoragePolicyAdmin`, `StoragePolicySatisfier`, `ExternalSPSContext`, `NameNodeConnector`, `DFSTestUtil.getNameNodeConnector`, `DFSTestUtil.waitExpectedStorageType`, `DistributedFileSystem`, and `StoragePolicySatisfierMode.EXTERNAL`.

## Control Flow
Setup enables external SPS mode, reduces the SPS DataNode cache refresh interval, starts a one-DataNode ARCHIVE/DISK cluster, obtains a `NameNodeConnector`, initializes a `StoragePolicySatisfier`, and starts it. Each test creates a file, confirms unspecified policy, sets COLD, runs `-satisfyStoragePolicy`, and waits for the block to move to ARCHIVE.

## State, Persistence, And Dependencies
State includes HDFS file block placement, storage policy metadata, the external SPS service thread, NameNode connector state, and DataNode storage-type reports. The field `externalSps` is intended for teardown but setup declares a local variable with the same name, so the field remains null and the satisfier may not be stopped explicitly.

## Integration Points
This tests CLI scheduling through NameNode APIs and the external SPS mover pipeline that changes block storage type.

## Risks
The shadowed `externalSps` local variable is a cleanup bug and can leak a service thread until cluster shutdown. The wait is timing-sensitive and depends on a single DataNode advertising ARCHIVE. URI-qualified expected output is exact-string sensitive.

## Test Signals
Signals include command return codes and messages, successful COLD policy set, scheduling output, and `waitExpectedStorageType` observing one ARCHIVE replica within 30 seconds.
