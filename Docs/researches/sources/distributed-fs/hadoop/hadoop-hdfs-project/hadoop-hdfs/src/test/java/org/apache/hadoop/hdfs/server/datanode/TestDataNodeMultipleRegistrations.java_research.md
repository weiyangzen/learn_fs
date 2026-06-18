# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMultipleRegistrations.java

## Purpose

`TestDataNodeMultipleRegistrations` validates DataNode registration and handshake behavior across federated NameNodes, HA nameservices, cluster-ID mismatches, invalid storage after reformat, and MiniDFSCluster support for adding NameNodes.

## Important APIs, Types, and Functions

The tests use `MiniDFSNNTopology`, `MiniDFSCluster`, `NameNode`, `FSImageTestUtil`, `BPOfferService`, `BPServiceActor`, `RunningState`, `StartupOption.FORMAT`, `DFSTestUtil.formatNameNode`, and `FSNamesystem` namespace directories. Helper `getNNSocketAddress` extracts the single BP service actor socket address for a `BPOfferService`.

## Control Flow

`test2NNRegistration` starts a two-NameNode federated cluster, reads block-pool IDs, cluster IDs, layout versions, and namespace IDs from both FSImages, verifies namespace IDs differ while cluster IDs match, inspects DataNode volume info, orders BPOfferServices by NameNode address, and checks each BPOS registered with the expected block pool and namespace. `testFedSingleNN` verifies a single NameNode registration and triggers a test block report, then shuts down and asserts all BPOfferServices are gone. `testClusterIdMismatch` adds a compatible third NameNode, then changes the startup cluster ID before adding a fourth and verifies the DataNode remains registered with only three.

`testClusterIdMismatchAtStartupWithHA` builds two nameservices where one has a bad cluster ID, then starts a DataNode and expects only one BPOfferService while the DataNode stays up. `testDNWithInvalidStorageWithHA` starts a valid HA nameservice, stops the DataNode and NameNodes, reformats NameNodes with a different cluster ID, restarts, and waits until BP service actors report `FAILED`. `testMiniDFSClusterWithMultipleNN` verifies NameNodes can be added to federated clusters but not to a non-federated cluster.

## State and Persistence Behavior

The suite validates persistent namespace identity fields: cluster ID, namespace ID, block pool ID, and layout version. It manipulates NameNode formatting and copies namespace directories to create invalid storage scenarios. DataNode BPOfferService lifecycle state is observed before and after cluster shutdown and restart.

## Dependencies and Integration Points

It integrates federated and HA NameNode topology, DataNode BPOfferService registration, FSImage metadata, MiniDFSCluster dynamic NameNode addition, NameNode formatting, and DataNode running-state transitions. It is a regression surface for multi-namespace DataNode identity safety.

## Risks and Edge Cases

The tests use sleeps for registration after adding NameNodes, which can be timing-sensitive. `StartupOption.FORMAT.setClusterId` is process-global state. Ordering of BPOfferServices is not guaranteed and is corrected manually. The invalid-storage test relies on reformatting and restarting NameNodes with copied namespace directories, which is sensitive to storage layout changes.

## Test Signals

Signals include exact BPOfferService counts, matching NameNode socket addresses and block-pool IDs, equal cluster IDs across valid namespaces, distinct namespace IDs, DataNode staying up with only valid services, BP service actor `FAILED` state after invalid storage, and expected `IOException` when adding a NameNode to a non-federated cluster.
