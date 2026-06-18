# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem.h

Purpose: declares `FileSystemImpl`, the concrete libhdfspp implementation of the public `FileSystem` interface. It defines the async and sync API surface, runtime worker controls, event hooks, options accessors, and private recursive listing helpers.

Important APIs and types: constructors accepting raw-transfer or shared `IoService`, `Connect`, `ConnectToDefaultFs`, `CancelPendingConnect`, `Open`, metadata APIs, mutation APIs, snapshot APIs, `SetFsEventCallback`, `AddWorkerThread`, `WorkerThreadCount`, `get_event_handlers`, `get_options`, `get_cluster_name`, plus nested `FindSharedState` and `FindOperationalState`.

Control flow: the class keeps asynchronous methods as the primary implementation and exposes synchronous counterparts implemented separately in `filesystem_sync.cc`. All file and metadata operations flow through the `NameNodeOperations nn_` member; open/read integration also uses `BadDataNodeTracker` and `FileHandle`.

State and persistence: `io_service_` is deliberately the first member so it is destroyed last. Other durable in-memory members include immutable `options_`, `client_name_`, mutable `cluster_name_`, `nn_`, `bad_node_tracker_`, `connect_callback_`, and `event_handlers_`. No state is persisted to disk.

Dependencies and integration: includes public libhdfspp headers, `namenode_operations.h`, `bad_datanode_tracker`, and reader `fileinfo`. This header ties the public HDFS client API to internal RPC, reader, and event subsystems.

Risks and test signals: because this header defines thread-safety expectations, tests should verify concurrent operations, destruction ordering, cancel/connect interactions, and sync/async parity. The raw `FileHandle *` ownership contract is important for leak and double-delete tests.
