# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/block_reader.h

Purpose: declares the block reader interface and implementation state for reading HDFS block data from DataNodes.

Important APIs and types: `CacheStrategy`, `DropBehindStrategy`, `EncryptionScheme`, `BlockReaderOptions`, abstract `BlockReader`, concrete `BlockReaderImpl`, async methods for read block/packet/request block, sync helpers `ReadPacket` and `RequestBlock`, and `CancelOperation`.

Control flow: consumers use `AsyncReadBlock` for a full block slice or manually call `AsyncRequestBlock` followed by packet reads. `BlockReaderImpl` tracks protocol state with enum values from `kOpen` through `kFinished`.

State and persistence: `BlockReaderImpl` stores DataNode connection, packet header, options, packet counters, checksum buffer, cancel state, and raw event handler pointer. State is per-operation and not thread-safe by design.

Dependencies and integration: includes data-transfer protobufs, status, async stream, cancel tracker, allocation helpers, and `DataNodeConnection`. It integrates with reader groups/file handles and DataNode connection factories.

Risks and test signals: the class is not thread-safe, so concurrent calls on one reader are unsafe. `event_handlers_` is a raw pointer derived from a shared pointer passed to the constructor, so owner lifetime must exceed reader operations. Tests should validate option defaults, state transitions, and cancellation behavior.
