# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFaultTolerant.java

## Purpose

`TestRouterFaultTolerant.java` verifies Router behavior for multi-destination mount points when one subcluster becomes unavailable. It builds two `MockNamenode` instances and two `Router` instances, registers subclusters through the state store, and checks write, list, content-summary, and read behavior across fault-tolerant and non-fault-tolerant mount settings. The source was read as a complete 675-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `MockNamenode`, `Router`, `RouterClient`, `MountTableManager`, `MultipleDestinationMountTableResolver`, `MembershipNamenodeResolver`, `DestinationOrder`, `RouterRpcClient.isUnavailableException`, and federation test helpers such as `createMountTableEntry`, `registerSubclusters`, `getFileSystem`, and `refreshRoutersCaches`. Key helpers are `setup`, `cleanup`, `updateMountPointFaultTolerant`, `testWriteWithFailedSubcluster(DestinationOrder)`, `checkDirectoriesFaultTolerant`, `checkFilesFaultTolerant`, `collectResults`, `TaskResults`, `getRandomRouter`, and `getRandomRouterFileSystem`.

## Control Flow

`setup` starts active mock namenodes for `ns0` and `ns1`, configures routers with RPC/admin/state-store support, uses router0 with partial listing disabled and router1 with partial listing enabled, registers all subclusters while excluding `ns1` from the active set, and creates a fixed thread pool. `testWriteWithFailedSubcluster` stops `ns1`, then runs write checks concurrently for `HASH_ALL`, `SPACE`, `RANDOM`, and `HASH` orderings. Each order creates a mount, tries directory and file creation before fault tolerance is enabled, updates the `MountTable` to `faultTolerant=true`, and repeats checks only for `FOLDER_ALL` orders; unsupported orders must reject the update. `testReadWithFailedSubcluster` creates a file, detects which namespace owns it, stops that namespace, and verifies opening the old path now yields an unavailable-cluster `RemoteException` rather than `FileNotFoundException`.

## State and Persistence Behavior

State lives in mock namenodes, router-local resolver caches, and state-store mount-table records. `updateMountPointFaultTolerant` mutates a persisted `MountTable` record through the admin API and explicitly refreshes router caches. The test intentionally creates per-call random `UserGroupInformation` instances to exercise router client concurrency. File and directory state is transient in mock namenode filesystems and is torn down by stopping mocks and routers.

## Dependencies and Integration Points

The test integrates Router RPC, admin APIs, mount-table state-store protocols (`GetMountTableEntriesRequest`, `UpdateMountTableEntryRequest`), membership registration, multi-destination resolver behavior, partial listing configuration, HDFS `FileSystem` operations, and remote exception classification. It is closely related to `TestRouterRpcMultiDestination#testSubclusterDown`.

## Risks and Edge Cases

The assertions depend on concurrent task scheduling and random router selection, so failures may expose timing-sensitive cache or resolver behavior. It also relies on mock namenode semantics, including zero-byte creates reporting a positive length through the mock. The `tasks` list is intentionally reused and cleared by `collectResults`; changing this helper can silently alter later list/content-summary checks. Fault-tolerant updates are valid only for all-destination orderings.

## Test Signals

Strong signals are successful mixed-result expectations before fault tolerance, all-success expectations after fault tolerance for supported orderings, explicit rejection for unsupported orderings, router0/router1 partial listing differences, and unavailable-cluster classification after the owning subcluster is stopped.
