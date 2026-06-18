# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/InternalDataNodeTestUtils.java

Purpose: this Mockito-enabled DataNode test utility contains internal helpers that should not leak to downstream MiniDFSCluster users. It complements `DataNodeTestUtils` by allowing spies and mocks.

Important APIs and types: `DataNode`, `FsDatasetSpi`, `DatanodeProtocolClientSideTranslatorPB`, `BPOfferService`, `BPServiceActor`, `NameNode`, `NamespaceInfo`, `HeartbeatResponse`, `NNHAStatusHeartbeat`, `StorageLocation`, Mockito spies/mocks/answers, and `Preconditions`.

Control flow: `mockDatanodeBlkPinning` wraps `dn.data` in a spy and overrides `getPinning` to return a fixed value. `spyOnBposToNN` finds the `BPOfferService` for a NameNode block pool, locates the service actor connected to the NameNode service RPC address, spies on the existing NameNode proxy, installs the spy, and returns it for call interception. `startDNWithMockNN` configures a fake HDFS URI, creates a local storage directory, mocks the NameNode protocol, returns registrations unchanged, supplies namespace info and active heartbeat responses, constructs a `DataNode` overriding `connectToNN`, and triggers an initial heartbeat.

State and persistence: helpers mutate DataNode internals by replacing dataset/proxy references. `startDNWithMockNN` deletes and recreates a supplied data directory and starts a real DataNode against mocked NameNode RPC.

Dependencies and integration points: this file is used for race and protocol tests that need to delay, assert, or fake DataNode-to-NameNode traffic. It directly integrates with BP service actor internals and should track those implementations closely.

Risks: replacing internal fields with spies can change behavior if methods are final or if concurrency expects the original object. `startDNWithMockNN` performs filesystem deletion on the provided path. Exact NameNode service address matching must remain consistent with BP actor setup.

Test signals: downstream tests using delayed block reports, mocked pinning, or mock NameNode startup provide coverage. Failures usually indicate DataNode protocol wiring or internal field layout changed.
