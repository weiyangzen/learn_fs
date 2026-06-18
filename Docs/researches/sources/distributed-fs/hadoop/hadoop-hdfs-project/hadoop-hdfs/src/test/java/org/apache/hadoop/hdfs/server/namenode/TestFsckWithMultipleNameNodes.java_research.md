# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsckWithMultipleNameNodes.java

**Purpose:** Verifies fsck works against federated HDFS deployments with multiple NameNodes and also through `viewfs` mount links.

**Important APIs and flow:** `createConf()` builds an `HdfsConfiguration` with short access-time precision and block-report intervals. `runTest()` creates a `MiniDFSCluster` using `MiniDFSNNTopology.simpleFederatedTopology(nNameNodes)`, applies `DFSTestUtil.setFederatedConfiguration()`, then uses a `Suite` helper to create one file per namespace through each namespace-specific `FileSystem`.

**Control flow:** The single test calls `runTest(3, 1, conf)`. For each NameNode namespace, the test creates `/tmp.txt`, waits for replication, invokes `TestFsck.runFsck()` on the fully qualified HDFS URL, and expects `Status: HEALTHY`. It then adds `viewfs` links with `ConfigUtil.addLink()` and repeats fsck against `viewfs:/mount/nn_i/tmp.txt`.

**State and persistence behavior:** State is limited to the MiniDFS federated namespace and the client-side `viewfs` configuration. No restart or edit-log replay is tested. The test does verify that each namespace's independent file can be resolved and checked without confusing the default filesystem or another NameNode namespace.

**Dependencies and integration points:** Integrates `DFSck` with federated `MiniDFSCluster`, `ClientProtocol`, `DFSTestUtil`, and `viewfs` link resolution. It also reuses `TestFsck.runFsck()` for output capture and return-code handling.

**Risks and test signals:** The assertions check text rather than structured status. The test uses one DataNode and replication derived as `max(1, nDataNodes - 1)`, so it is focused on routing/namespace selection rather than redundancy. A pass signals that fsck can target explicit HDFS namespace URIs and `viewfs` links in a multi-NameNode configuration.
