# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderRemote.java

## Purpose
`BlockReaderRemote` is the packet-protocol HDFS block reader used when reading from a DataNode over a `Peer` connection. It sends an `OP_READ_BLOCK` request, consumes DataTransferProtocol packets, verifies checksums when requested, and optionally returns the connection to `PeerCache` after a clean read-status response.

## Important APIs, types, and functions
The class implements `BlockReader`. `newBlockReader(...)` sends the read request through `Sender.readBlock`, parses `BlockOpResponseProto`, extracts `ReadOpChecksumInfoProto`, validates the first chunk offset, and creates the reader. `read(byte[],...)` and `read(ByteBuffer)` expose bytes from `curDataSlice`. `readNextPacket()` receives a packet with `PacketReceiver`, validates its `PacketHeader`, verifies chunk checksums, skips prefix bytes before `startOffset`, and when the requested byte count is satisfied reads the trailing empty packet and sends `CHECKSUM_OK` or `SUCCESS`. `sendReadResult` and static `writeReadResult` serialize `ClientReadStatusProto`. `checkSuccess` delegates block operation status validation to `DataTransferProtoUtil`.

## Control flow
Creation wraps the peer output stream in a buffered `DataOutputStream`, sends a read-block operation containing the block, token, client name, start offset, requested length, checksum flag, and caching strategy, then reads the server response from the peer input stream. During reads, if no current data slice remains and more transfer bytes are needed, the reader pulls the next packet. Each packet advances `lastSeqNo`, reduces `bytesNeededToFinish`, verifies checksums against the packet checksum slice and offset, and positions the data slice so callers only see requested bytes. At the logical end of the read, the reader consumes the mandatory zero-length last packet before sending the final status. `skip` advances over already received packet data and reads more packets as needed.

## State and persistence behavior
Persistent state is only connection/session state: the `Peer`, `DatanodeID`, optional `PeerCache`, `PacketReceiver`, current packet data slice, checksum parameters, current sequence number, start offset, remaining bytes to finish, and whether the final status has been sent. `close` closes packet resources, clears checksum/start state, and returns the peer to the cache only if a status code was successfully sent; otherwise it closes the peer to avoid reusing a connection in an uncertain protocol state.

## Dependencies and integration points
It depends on `Peer`, `PeerCache`, DataTransferProtocol classes (`Sender`, `PacketHeader`, `PacketReceiver`, protobuf status/checksum messages), `DataChecksum`, `ExtendedBlock`, block tokens, `CachingStrategy`, and HDFS client remote-buffer configuration. It is consumed by `DFSInputStream` block-reader selection logic and is the remote counterpart to short-circuit readers.

## Risks and test signals
Key risks are packet sequence/header validation, correct handling of padded bytes before `startOffset`, checksum error offset reporting, draining the trailing empty packet, and peer-cache reuse only after a clean final status. Tests should include successful checksum and no-checksum reads, mid-chunk start offsets, packet boundary reads, short skips, malformed packet headers, invalid first chunk offsets, DataNode error responses, send-status failures, and verifying that failed or incomplete reads close rather than cache peers.
