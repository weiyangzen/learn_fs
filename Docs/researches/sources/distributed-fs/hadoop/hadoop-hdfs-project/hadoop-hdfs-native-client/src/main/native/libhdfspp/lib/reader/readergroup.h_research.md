# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/readergroup.h

Purpose: declares the `ReaderGroup` helper for tracking a set of active block readers without owning them.

Important APIs and types: `ReaderGroup`, `AddReader`, `GetLiveReaders`, and private `ClearDeadReaders`.

Control flow: public methods lock `state_lock_`; readers are stored as weak pointers and promoted when live readers are requested.

State and persistence: `std::vector<std::weak_ptr<BlockReader>> readers_` and `std::recursive_mutex state_lock_`. No disk persistence.

Dependencies and integration: depends on `reader/block_reader.h`, memory/vector/mutex. It integrates with components that need group-level visibility into outstanding read operations.

Risks and test signals: weak ownership means group membership disappears when external owners release readers. Tests should validate that stale weak pointers are removed and that live-reader snapshots remain valid after lock release.
