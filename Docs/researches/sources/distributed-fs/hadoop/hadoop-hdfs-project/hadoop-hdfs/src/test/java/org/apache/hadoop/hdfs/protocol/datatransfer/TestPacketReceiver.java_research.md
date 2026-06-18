<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/TestPacketReceiver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/TestPacketReceiver.java

Purpose: Tests `PacketReceiver` packet sizing, parsing of checksum/data slices, and one-call packet mirroring.

Important APIs/types/functions: `PacketHeader`, `PacketReceiver.receiveNextPacket`, `getDataSlice`, `getChecksumSlice`, `getHeader`, `mirrorPacketTo`, `MAX_PACKET_SIZE`, and `HdfsClientConfigKeys.DFS_DATA_TRANSFER_MAX_PACKET_SIZE_DEFAULT`.

Control flow: `prepareFakePacket` writes a header, checksum bytes, and data bytes into a byte array. `testPacketSize` pins max-packet default alignment. `testReceiveAndMirror` reuses one receiver for packets of different sizes to force buffer reallocation, then `doTestReceiveAndMirror` validates parsed slices, header fields, and mirrored output bytes. Mockito verifies mirroring writes the full packet in one `OutputStream.write` call.

State and persistence behavior: In-memory byte buffers only. The receiver internally resizes and reuses buffers across packet sizes.

Dependencies and integration points: Guards DataTransferProtocol packet parsing and forwarding, relevant for DataNode pipeline mirroring and TCP/Nagle interaction avoidance.

Risks: The one-write assertion couples implementation to performance behavior. Packet construction must stay in sync with `PacketHeader` layout.

Test signals: Passing means packet slices match original payloads, header metadata is preserved, and mirror output is byte-identical with a single write call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/TestPacketReceiver.java -->
