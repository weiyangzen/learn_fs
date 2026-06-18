# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataXceiverBackwardsCompat.java

Purpose: mock-based compatibility test proving `DataXceiver.writeBlock` can process Hadoop 2.x-style write-block calls that omit newer storage ID and target storage type data far enough to send downstream data.

Important APIs and types: `DataXceiver`, `DataXceiverServer`, `BlockReceiver`, `Peer`, `PeerServer`, `SaslDataTransferClient`, `FsDatasetSpi`, `ReplicaHandler`, `DatanodeInfo`, `ExtendedBlock`, `DataChecksum`, block tokens, and an inner `NullDataNode` subclass. `NullDataNode` installs mocked dataset/SASL fields and starts a one-shot local `NullServer`.

Control flow: `testBackwardsCompat` builds a mocked peer, a byte output stream, a local acceptor port, a `NullDataNode`, and a spied `DataXceiver`. It stubs `getBlockReceiver`, creates token/checksum/datanode-info mocks, and calls `writeBlock` with `new String[0]` storage IDs and null/empty optional arrays. Exceptions are tolerated after the call has progressed far enough; the test fails if no bytes are written to the downstream output because that means the compatibility path aborted too early.

State and persistence behavior: state is in mocked objects, a local socket, and a byte output buffer. Integration points are DataXceiver pipeline setup, SASL send, block receiver creation, and datatransfer protocol serialization. Risks include partial mocking brittleness, one-shot server timing, and reliance on "some bytes written" as the success boundary rather than full protocol completion. Test signals are non-empty downstream output and absence of early exception before serialization.
