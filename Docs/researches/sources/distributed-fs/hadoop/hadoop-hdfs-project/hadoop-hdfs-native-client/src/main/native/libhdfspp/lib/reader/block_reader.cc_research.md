# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/block_reader.cc

Purpose: implements DataNode block-read protocol handling. It sends `OP_READ_BLOCK`, reads DataNode packet headers/checksums/padding/data, emits final read acknowledgments, and exposes async and sync packet/block read APIs.

Important APIs and functions: `ReadBlockProto`, `AsyncRequestBlock`, `RequestBlock`, continuation structs `ReadPacketHeader`, `ReadChecksum`, `ReadPadding`, `ReadData`, `AckRead`, `AsyncReadPacket`, `ReadPacket`, `RequestBlockContinuation`, `ReadBlockContinuation`, `AsyncReadBlock`, and `CancelOperation`.

Control flow: `AsyncRequestBlock` serializes the data-transfer header and `OpReadBlockProto`, writes it, reads `BlockOpResponseProto`, handles checksum info, and transitions to `kReadPacketHeader`. `AsyncReadPacket` runs a continuation pipeline: header, checksum, optional padding, user-data read, then final ack if `bytes_to_read_` is exhausted. `AsyncReadBlock` first requests the block, then repeatedly reads packets until the user buffer is filled.

State and persistence: per-reader state includes DataNode connection, current packet header, state enum, options, packet length, data-read counters, chunk padding, bytes remaining, checksum buffer, cancel handle, and event hooks. No disk state. Continuations hold shared DataNode connections to avoid pending-ASIO lifetime races.

Dependencies and integration: depends on `DataNodeConnection`, data-transfer protobufs, continuation framework, Boost ASIO, logging, event simulation hooks, and HDFS block tokens. It is used by file reading paths after NameNode block location lookup.

Risks and test signals: packet parsing uses fixed max header buffer and asserts parse success; malformed packets should be tested. Padding math depends on checksum chunk offset. `ReadData` currently requests `header_.datalen() - packet_data_read_bytes_` into the caller buffer, so buffer sizing and partial-packet behavior are critical. Cancellation currently forwards to `dn_->Cancel`; tests should cover cancel during each pipeline stage and connection lifetime after HDFS-10931-style races.
