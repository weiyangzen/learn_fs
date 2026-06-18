# subset-b-007437 grouped research

Work item `subset-b-007437` covers libhdfspp filesystem, NameNode RPC, DataNode reader, protobuf-generation, and RPC/SASL implementation files. Each section preserves the source path in its title and is wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem.cc

Purpose: implements the public asynchronous `FileSystem` facade for libhdfspp. It constructs `FileSystemImpl`, resolves effective users, connects to NameNodes, opens files, exposes metadata/mutation/snapshot APIs, converts block-location protobufs into public objects, and implements recursive listing/find behavior.

Important APIs and functions: `FileSystem::New`, `get_effective_user_name`, `FileSystemImpl::Connect`, `ConnectToDefaultFs`, `CancelPendingConnect`, `Open`, `GetBlockLocations`, `GetListing`, `Find`, permission/replication validators, mutators such as `Mkdirs`, `Delete`, `Rename`, `SetPermission`, `SetOwner`, and snapshot calls. `FindSharedState` and `FindOperationalState` hold recursive search state.

Control flow: construction creates an `IoService`, random client name, `NameNodeOperations`, bad DataNode tracker, and event handlers. `Connect` resolves HA or single NameNode configuration, stores `cluster_name_`, then delegates to `NameNodeOperations::Connect`. Most filesystem APIs validate cheap client-side invariants and forward to `nn_`. `Open` first retrieves full block locations and returns a `FileHandleImpl` on success. `GetListing` paginates via `GetListingShim`; `Find` starts from `/`, expands path globs before name matching, and launches additional async listings for matched directories.

State and persistence: persistent state is in-memory only: `io_service_`, `options_`, `client_name_`, `cluster_name_`, `nn_`, `bad_node_tracker_`, swappable connect callback, and event handlers. `Find` uses shared atomics and a mutex to coordinate outstanding async listing requests. Destruction stops the `IoService`; callers must close open files before destroying the filesystem.

Dependencies and integration: depends on `NameNodeOperations`, `FileHandleImpl`, HDFS public types, URI/name-node resolution helpers, `BadDataNodeTracker`, Boost ASIO, platform user/glob helpers, and libhdfs event hooks. It is the integration point between public HDFS API calls and generated NameNode RPC operations.

Risks and test signals: async callbacks frequently capture `this`, so object lifetime during shutdown/cancel is critical. `CancelPendingConnect` swaps callbacks and posts cancellation, which should be tested for races with successful connection. `GetListing` assumes non-empty `path` before `path.back()`. Recursive `Find` has concurrent callback ordering, outstanding-counter, pagination, and user-abort behavior that need stress tests. High-bit checks on protobuf int64-compatible fields and validation of permission/replication ranges are important boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem.h

Purpose: declares `FileSystemImpl`, the concrete libhdfspp implementation of the public `FileSystem` interface. It defines the async and sync API surface, runtime worker controls, event hooks, options accessors, and private recursive listing helpers.

Important APIs and types: constructors accepting raw-transfer or shared `IoService`, `Connect`, `ConnectToDefaultFs`, `CancelPendingConnect`, `Open`, metadata APIs, mutation APIs, snapshot APIs, `SetFsEventCallback`, `AddWorkerThread`, `WorkerThreadCount`, `get_event_handlers`, `get_options`, `get_cluster_name`, plus nested `FindSharedState` and `FindOperationalState`.

Control flow: the class keeps asynchronous methods as the primary implementation and exposes synchronous counterparts implemented separately in `filesystem_sync.cc`. All file and metadata operations flow through the `NameNodeOperations nn_` member; open/read integration also uses `BadDataNodeTracker` and `FileHandle`.

State and persistence: `io_service_` is deliberately the first member so it is destroyed last. Other durable in-memory members include immutable `options_`, `client_name_`, mutable `cluster_name_`, `nn_`, `bad_node_tracker_`, `connect_callback_`, and `event_handlers_`. No state is persisted to disk.

Dependencies and integration: includes public libhdfspp headers, `namenode_operations.h`, `bad_datanode_tracker`, and reader `fileinfo`. This header ties the public HDFS client API to internal RPC, reader, and event subsystems.

Risks and test signals: because this header defines thread-safety expectations, tests should verify concurrent operations, destruction ordering, cancel/connect interactions, and sync/async parity. The raw `FileHandle *` ownership contract is important for leak and double-delete tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem_sync.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem_sync.cc

Purpose: provides blocking `FileSystemImpl` methods by wrapping the asynchronous filesystem API with `std::promise` and `std::future`. It intentionally contains boilerplate sync shims rather than core filesystem logic.

Important APIs and functions: sync variants of `Connect`, `ConnectToDefaultFs`, `Open`, `GetBlockLocations`, `GetPreferredBlockSize`, `SetReplication`, `SetTimes`, `GetFileInfo`, `GetContentSummary`, `GetFsStats`, `GetListing`, `Mkdirs`, `Delete`, `Rename`, `SetPermission`, `SetOwner`, `Find`, and snapshot operations.

Control flow: each method creates a promise, passes a callback to the async method, waits on the future, then copies successful output data into caller-provided references or pointers. Listing and find accumulate multi-page callback results until `has_more`/`has_more_results` becomes false.

State and persistence: no independent persistent state. Temporary promises, futures, tuples, and output accumulators live only for the duration of the blocking call. `Find` keeps a local status that records the first async error.

Dependencies and integration: depends on `filesystem.h`, futures, tuples, and the async `FileSystemImpl` implementation. These functions require `IoService` worker threads to be running; otherwise futures may never complete.

Risks and test signals: sync methods can deadlock if called from an `IoService` worker that is needed to satisfy the async operation, or if no worker thread exists. Pointer validation is inconsistent: `GetBlockLocations`, `GetListing`, and `Find` validate output pointers, while other reference outputs assume validity. `Open` deletes a non-null handle on error and should be leak-tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem_sync.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/namenode_operations.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/namenode_operations.cc

Purpose: implements `NameNodeOperations`, the translation layer between filesystem calls and `ClientNamenodeProtocol` protobuf RPCs. It builds request protobufs, dispatches generated RPC stub methods, and converts response protobufs into libhdfspp public data structures and statuses.

Important APIs and functions: `Connect`, `CancelPendingConnect`, `GetBlockLocations`, `GetPreferredBlockSize`, `SetReplication`, `SetTimes`, `GetFileInfo`, `GetContentSummary`, `GetFsStats`, `GetListing`, `Mkdirs`, `Delete`, `Rename`, `SetPermission`, `SetOwner`, snapshot operations, `SetFsEventCallback`, and conversion helpers for file status, content summary, directory listing, and fs stats.

Control flow: each operation validates required path/argument values, populates the corresponding Hadoop protobuf request, allocates a shared response, invokes `namenode_.Method`, and in the callback maps server response fields into libhdfspp objects. Boolean result methods translate successful RPCs with false/missing result into `PathNotFound` or `InvalidArgument` because NameNode responses may not include detailed reasons.

State and persistence: holds only in-memory RPC engine/stub state inherited from the header. Request/response protobufs are per-call objects captured by callbacks. No disk persistence.

Dependencies and integration: depends on generated Hadoop HDFS protobuf classes and generated `.hrpc.inl` stubs. It sits below `FileSystemImpl` and above `RpcEngine`, so changes here affect all filesystem metadata and namespace operations.

Risks and test signals: “OK but missing field” behavior is deliberately normalized and should be covered for nonexistent files/directories. `GetBlockLocations` appends an incomplete last block when present, affecting file length and read planning. Directory listing path composition appends `/`, so root and child path edge cases need tests. High-bit checks prevent protobuf negative-value errors for uint64 offsets/lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/namenode_operations.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/namenode_operations.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/namenode_operations.h

Purpose: declares `NameNodeOperations`, the thread-safe NameNode communication abstraction owned by `FileSystemImpl`. It wraps `RpcEngine` and generated `ClientNamenodeProtocol` methods.

Important APIs and types: constructor accepting `IoService`, `Options`, client/user/protocol data; `Connect`; `CancelPendingConnect`; block, metadata, listing, mutation, owner/permission, and snapshot methods; event callback setter; static conversion helpers.

Control flow: callers invoke typed C++ methods; implementation builds protobuf calls against `namenode_`, which was generated by `protoc_gen_hrpc.cc` and delegates to `RpcEngine::AsyncRpc`.

State and persistence: owns `io_service_`, shared `RpcEngine`, generated `ClientNamenodeProtocol namenode_`, and a copy of `Options`. No persistent external state.

Dependencies and integration: includes Hadoop NameNode protobufs, `rpc_engine.h`, public stat/content/fsinfo types, NameNode resolution types, and generated `ClientNamenodeProtocol.hrpc.inl`. This header defines the contract between filesystem semantics and wire RPC.

Risks and test signals: comments note eventual retry/failover ownership, but current failover is in `RpcEngine`. Tests should validate that all public filesystem operations map to the correct RPC method and response conversion, especially for error statuses and optional protobuf fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/namenode_operations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/proto/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/proto/CMakeLists.txt

Purpose: defines protobuf and generated-HRPC build steps for libhdfspp. It generates C++ protobuf sources from Hadoop/HDFS `.proto` files, builds the custom `protoc-gen-hrpc` plugin, and creates the `proto` library.

Important APIs and functions: `protobuf_generate_cpp`, executable target `protoc-gen-hrpc`, custom CMake function `GEN_HRPC`, `gen_hrpc(HRPC_SRCS ClientNamenodeProtocol.proto)`, object library `proto_obj`, and final library `proto`.

Control flow: CMake builds protobuf outputs for many Hadoop protocol files, builds the HRPC plugin, then `GEN_HRPC` invokes `protoc` with `--plugin=protoc-gen-hrpc` and `--hrpc_out` to produce `.hrpc.inl` stubs in the binary directory.

State and persistence: generated build artifacts live under `CMAKE_CURRENT_BINARY_DIR`; no runtime state. The function appends include paths from `PROTOBUF_IMPORT_DIRS` while avoiding duplicates.

Dependencies and integration: depends on protobuf compiler/library targets, Hadoop proto directories, optional `copy_hadoop_files`, and `${protobuf_ABSL_USED_TARGETS}`. Downstream `fs` and `rpc` code depends on generated protobuf and HRPC files.

Risks and test signals: duplicate `datatransfer.proto` appears in the generation list and may be benign or build-system-sensitive. Build tests should verify clean builds, incremental regeneration when proto/plugin changes, and generated include visibility for `ClientNamenodeProtocol.hrpc.inl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/proto/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/proto/protoc_gen_hrpc.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/proto/protoc_gen_hrpc.cc

Purpose: implements a protobuf compiler plugin that generates lightweight C++ HRPC service stubs. The generated stubs call `hdfs::RpcEngine::AsyncRpc` for each protobuf service method.

Important APIs and types: `StubGenerator` subclass of `google::protobuf::compiler::CodeGenerator`, `Generate`, `EmitService`, `EmitMethod`, and `main` invoking `PluginMain`.

Control flow: for every service in a `.proto` file, `Generate` opens `<proto-name>.hrpc.inl`, writes a generated class with a shared `RpcEngine`, and emits one inline method per protobuf method. Each generated method takes a request message, shared response message, and callback, then passes the raw method name to `AsyncRpc`.

State and persistence: no runtime persistence beyond generated source files emitted through `GeneratorContext`. The generated class stores a shared pointer to `RpcEngine`.

Dependencies and integration: depends on protobuf compiler APIs and local `protobuf/cpp_helpers.h` helpers such as `StripProto` and `ToCamelCase`. Its output is included by `namenode_operations.h`.

Risks and test signals: generator output is simple and method-name-sensitive; tests should diff generated stubs for expected methods after proto updates. It assumes service names are valid C++ class names and does not generate include guards or namespaces itself in this file, so consuming context matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/proto/protoc_gen_hrpc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/CMakeLists.txt

Purpose: defines the libhdfspp reader build target for DataNode block reading and data-transfer helpers.

Important APIs and targets: `reader_obj` object library built from `block_reader.cc`, `datatransfer.cc`, and `readergroup.cc`; dependency on `proto`; final `reader` library from object files.

Control flow: CMake compiles reader sources after generated protobuf artifacts are available, then exposes them through a static/object-composed `reader` library.

State and persistence: build metadata only; no runtime state.

Dependencies and integration: depends on the `proto` target because reader code uses `datatransfer.pb.h` and HDFS block protobufs. The library integrates with file handles and DataNode connections elsewhere in libhdfspp.

Risks and test signals: build tests should ensure `proto` generation completes before reader compilation and optional platform/link settings from parent CMake files remain sufficient for Boost ASIO/protobuf use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/block_reader.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/block_reader.cc

Purpose: implements DataNode block-read protocol handling. It sends `OP_READ_BLOCK`, reads DataNode packet headers/checksums/padding/data, emits final read acknowledgments, and exposes async and sync packet/block read APIs.

Important APIs and functions: `ReadBlockProto`, `AsyncRequestBlock`, `RequestBlock`, continuation structs `ReadPacketHeader`, `ReadChecksum`, `ReadPadding`, `ReadData`, `AckRead`, `AsyncReadPacket`, `ReadPacket`, `RequestBlockContinuation`, `ReadBlockContinuation`, `AsyncReadBlock`, and `CancelOperation`.

Control flow: `AsyncRequestBlock` serializes the data-transfer header and `OpReadBlockProto`, writes it, reads `BlockOpResponseProto`, handles checksum info, and transitions to `kReadPacketHeader`. `AsyncReadPacket` runs a continuation pipeline: header, checksum, optional padding, user-data read, then final ack if `bytes_to_read_` is exhausted. `AsyncReadBlock` first requests the block, then repeatedly reads packets until the user buffer is filled.

State and persistence: per-reader state includes DataNode connection, current packet header, state enum, options, packet length, data-read counters, chunk padding, bytes remaining, checksum buffer, cancel handle, and event hooks. No disk state. Continuations hold shared DataNode connections to avoid pending-ASIO lifetime races.

Dependencies and integration: depends on `DataNodeConnection`, data-transfer protobufs, continuation framework, Boost ASIO, logging, event simulation hooks, and HDFS block tokens. It is used by file reading paths after NameNode block location lookup.

Risks and test signals: packet parsing uses fixed max header buffer and asserts parse success; malformed packets should be tested. Padding math depends on checksum chunk offset. `ReadData` currently requests `header_.datalen() - packet_data_read_bytes_` into the caller buffer, so buffer sizing and partial-packet behavior are critical. Cancellation currently forwards to `dn_->Cancel`; tests should cover cancel during each pipeline stage and connection lifetime after HDFS-10931-style races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/block_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/block_reader.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/block_reader.h

Purpose: declares the block reader interface and implementation state for reading HDFS block data from DataNodes.

Important APIs and types: `CacheStrategy`, `DropBehindStrategy`, `EncryptionScheme`, `BlockReaderOptions`, abstract `BlockReader`, concrete `BlockReaderImpl`, async methods for read block/packet/request block, sync helpers `ReadPacket` and `RequestBlock`, and `CancelOperation`.

Control flow: consumers use `AsyncReadBlock` for a full block slice or manually call `AsyncRequestBlock` followed by packet reads. `BlockReaderImpl` tracks protocol state with enum values from `kOpen` through `kFinished`.

State and persistence: `BlockReaderImpl` stores DataNode connection, packet header, options, packet counters, checksum buffer, cancel state, and raw event handler pointer. State is per-operation and not thread-safe by design.

Dependencies and integration: includes data-transfer protobufs, status, async stream, cancel tracker, allocation helpers, and `DataNodeConnection`. It integrates with reader groups/file handles and DataNode connection factories.

Risks and test signals: the class is not thread-safe, so concurrent calls on one reader are unsafe. `event_handlers_` is a raw pointer derived from a shared pointer passed to the constructor, so owner lifetime must exceed reader operations. Tests should validate option defaults, state transitions, and cancellation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/block_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer.cc

Purpose: implements utility functions for DataTransfer SASL/encryption handshake messages.

Important APIs and functions: `DataTransferSaslStreamUtil::ConvertToStatus` and `PrepareInitialHandshake`.

Control flow: `ConvertToStatus` maps `DataTransferEncryptorMessageProto` statuses to libhdfspp `Status`: unknown key becomes `InvalidEncryptionKeyException`, generic error becomes `Status::Error`, and success copies payload. `PrepareInitialHandshake` initializes a success status with empty payload.

State and persistence: stateless helper functions only.

Dependencies and integration: depends on `datatransfer.h`, `hdfspp/status.h`, and generated DataTransfer protobufs. Used by `DataTransferSaslStream` template code in `datatransfer_impl.h`.

Risks and test signals: tests should verify all DataTransfer encryptor status mappings and payload clearing/copying. Unknown future status values currently fall through as success, which is a compatibility risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer.h

Purpose: declares DataTransfer protocol constants and a SASL-wrapping DataNode stream template.

Important APIs and types: constants `kDataTransferVersion` and `kDataTransferSasl`, enum `Operation` with write/read block opcodes, and template `DataTransferSaslStream<Stream>` implementing `DataNodeConnection`.

Control flow: the wrapper forwards async reads/writes to the underlying stream, exposes `Handshake`, stubs `Connect` with a TODO, and declares `Cancel`. Implementation details are included from `datatransfer_impl.h`.

State and persistence: stores shared wrapped stream and `DigestMD5Authenticator`. No disk persistence.

Dependencies and integration: depends on data-transfer protobufs, SASL authenticator, async stream, and `DataNodeConnection`. It is intended to secure DataNode data-transfer streams.

Risks and test signals: `Connect` is currently a no-op TODO and `Cancel` is implemented as empty in the template impl, so secured DataTransfer integration is incomplete. Tests should distinguish direct stream forwarding from actual SASL handshake coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer_impl.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer_impl.h

Purpose: implements the template handshake pipeline for `DataTransferSaslStream`.

Important APIs and types: utility declarations for status conversion and initial handshake, nested continuations `Authenticator` and `ReadSaslMessage`, template method `Handshake`, and `Cancel`.

Control flow: `Handshake` writes the DataTransfer SASL magic number, sends an initial empty-success protobuf, reads the server SASL message, evaluates it with `DigestMD5Authenticator`, sends the response protobuf, and reads the final server message. The pipeline uses protobuf delimited-message continuations.

State and persistence: handshake state is temporary in a pipeline `State` struct containing request/response protobufs, payload strings, and stream. The stream and authenticator are object state from `datatransfer.h`.

Dependencies and integration: depends on continuation framework, ASIO write helpers, protobuf continuations, SASL authenticator, Boost ASIO, and generated DataTransfer protobufs.

Risks and test signals: encryption scheme handling is TODO, and `Authenticator::Run` always calls `next(Status::OK())` even if authentication failed, relying on message status rather than local status propagation. `Cancel` is empty. Tests should cover successful/failed challenge-response, malformed delimited protobufs, and handshake cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/datatransfer_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/fileinfo.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/fileinfo.h

Purpose: defines internal file block-location metadata used by file handles and readers after NameNode lookup.

Important APIs and types: `struct FileInfo` with `file_length_`, `last_block_complete_`, `under_construction_`, and `std::vector<LocatedBlockProto> blocks_`.

Control flow: `NameNodeOperations::GetBlockLocations` populates this structure; `FileSystemImpl::Open` passes it to `FileHandleImpl`; block readers consume located block data to contact DataNodes.

State and persistence: plain in-memory aggregate with protobuf block copies. No methods and no disk persistence.

Dependencies and integration: depends on `hdfs.pb.h` for `LocatedBlockProto`. Bridges NameNode metadata and reader/file-handle code.

Risks and test signals: correctness depends on NameNode conversion logic, especially incomplete last-block handling and file length adjustment. Tests should verify empty files, under-construction files, and multi-block files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/fileinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/readergroup.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/readergroup.cc

Purpose: implements `ReaderGroup`, a small helper tracking live `BlockReader` instances by weak reference.

Important APIs and functions: `AddReader`, `GetLiveReaders`, and `ClearDeadReaders`.

Control flow: adding a reader first clears expired weak pointers, then stores a weak reference to the new reader. `GetLiveReaders` locks and promotes non-expired readers. `ClearDeadReaders` uses `remove_if` to erase expired entries.

State and persistence: maintains an in-memory vector of `weak_ptr<BlockReader>` guarded by `recursive_mutex`.

Dependencies and integration: depends on `readergroup.h`, `<algorithm>`, and `BlockReader`. It can support coordinated cancellation/inspection of active readers by higher-level file-handle code.

Risks and test signals: recursive mutex hides nested locking from `AddReader` to `ClearDeadReaders`; tests should verify expired-reader cleanup and concurrent add/list behavior. Since only weak refs are stored, callers must own readers elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/readergroup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/readergroup.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/readergroup.h

Purpose: declares the `ReaderGroup` helper for tracking a set of active block readers without owning them.

Important APIs and types: `ReaderGroup`, `AddReader`, `GetLiveReaders`, and private `ClearDeadReaders`.

Control flow: public methods lock `state_lock_`; readers are stored as weak pointers and promoted when live readers are requested.

State and persistence: `std::vector<std::weak_ptr<BlockReader>> readers_` and `std::recursive_mutex state_lock_`. No disk persistence.

Dependencies and integration: depends on `reader/block_reader.h`, memory/vector/mutex. It integrates with components that need group-level visibility into outstanding read operations.

Risks and test signals: weak ownership means group membership disappears when external owners release readers. Tests should validate that stale weak pointers are removed and that live-reader snapshots remain valid after lock release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/readergroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/CMakeLists.txt

Purpose: defines the RPC library build target and conditionally includes SASL backend implementations.

Important APIs and targets: `rpc_object_items`, conditional appends for `cyrus_sasl_engine.cc` and `gsasl_engine.cc`, object library `rpc_obj`, dependency on `proto`, final library `rpc`, include directories, and Boost linkage.

Control flow: CMake collects common RPC sources plus x-platform objects, conditionally appends SASL sources based on configuration flags, builds object files after protobuf generation, and exposes the `rpc` library.

State and persistence: build configuration only.

Dependencies and integration: depends on `proto`, Boost libraries, local include paths, and optional Cyrus/GSASL availability. This build target feeds NameNode RPC functionality used by filesystem operations.

Risks and test signals: SASL compile paths depend on CMake flags and external libraries; CI should cover unsecured, Cyrus SASL, and GSASL builds where supported. Missing `sasl_protocol.cc` from this work item is still included in the build target, so link/test failures may arise outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/cyrus_sasl_engine.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/cyrus_sasl_engine.cc

Purpose: implements the Cyrus SASL-backed `SaslEngine` for Kerberos/GSSAPI authentication.

Important APIs and functions: `CySaslEngine` constructor/destructor, `InitCyrusSasl`, `Start`, `Step`, `Finish`, `SaslError`, error helpers, callbacks `sasl_my_log`, `sasl_getopt`, `get_path`, `get_name`, `getrealm`, and singleton `CyrusPerProcessData`.

Control flow: process-wide Cyrus is lazily initialized under the GSSAPI mutex. Per-connection `sasl_client_new` uses callbacks bound to the engine. `Start` calls `sasl_client_start` for the chosen mechanism, transitions to success or waiting-for-data, and returns the first token. `Step` feeds server data to `sasl_client_step` and returns the next token. `Finish` disposes the SASL connection.

State and persistence: per-engine state includes `sasl_conn_t *conn_` and per-connection callbacks. `CyrusPerProcessData` is a Meyers singleton that initializes and later calls `sasl_done`. No disk persistence, but global library state is process-wide.

Dependencies and integration: depends on Cyrus SASL, `hdfspp/locks.h`, logging, and base `SaslEngine`. Integrated by `SaslProtocol` when the build enables Cyrus SASL.

Risks and test signals: global SASL/GSSAPI locking is critical. Callback functions return pointers into optional strings and assume principal/id are set for selected callback IDs. `PLUGINDIR` is hard-coded to `/usr/local/lib/sasl2`. Tests should cover initialization failure, missing credentials, multi-threaded auth, state transitions, and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/cyrus_sasl_engine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/cyrus_sasl_engine.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/cyrus_sasl_engine.h

Purpose: declares `CySaslEngine`, the Cyrus SASL implementation of the abstract `SaslEngine`.

Important APIs and types: constructor/destructor, overrides `Start`, `Step`, `Finish`, private `InitCyrusSasl`, `SaslError`, `sasl_conn_t *conn_`, and per-connection callback vector. Callback functions are friends so they can read engine credential fields.

Control flow: callers configure base SASL info, choose a mechanism, then call `Start`/`Step`/`Finish`. Implementation state follows the base `SaslEngine::State` model.

State and persistence: owns a Cyrus connection pointer and callback vector. No persistent storage.

Dependencies and integration: includes Cyrus `<sasl/sasl.h>` and base `sasl_engine.h`; included only when the build enables Cyrus SASL.

Risks and test signals: raw `sasl_conn_t *` ownership must be disposed exactly once. Friend callbacks couple external C callback behavior to internal optional credential state; tests should exercise absent optional values and destructor-after-partial-init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/cyrus_sasl_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/gsasl_engine.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/gsasl_engine.cc

Purpose: implements the GNU SASL-backed `SaslEngine` for GSSAPI/Kerberos authentication.

Important APIs and functions: `GSaslEngine::~GSaslEngine`, `gsasl_new`, `Start`, `init_kerberos`, `Step`, `Finish`, plus helpers `rc_to_status` and `base64_encode`.

Control flow: `Start` initializes GSASL context, creates a client session for the chosen mechanism, sets Kerberos properties, marks state waiting-for-data, and immediately runs `Step` with the initial challenge. `Step` calls `gsasl_step`, returns output tokens for `GSASL_NEEDS_MORE`/`GSASL_OK`, and updates success/failure state. `Finish` cleans up session and context.

State and persistence: owns raw `Gsasl *ctx_` and `Gsasl_session *session_`, protected during library calls by the GSSAPI mutex. No disk persistence.

Dependencies and integration: depends on GNU SASL, `hdfspp/locks.h`, logging, and base `SaslEngine`. Built conditionally by RPC CMake.

Risks and test signals: `Start` ignores the return value of `gsasl_new`, so failed initialization can lead to null-context use. `init_kerberos` calls `principal_.value()` with a TODO, so missing principal can throw or fail unexpectedly. `base64_encode` is unused. Tests should cover missing principal, init failure, concurrent auth, and cleanup on partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/gsasl_engine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/gsasl_engine.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/gsasl_engine.h

Purpose: declares `GSaslEngine`, the GNU SASL implementation of `SaslEngine`.

Important APIs and types: default constructor initializing `ctx_` and `session_` to null, destructor, overrides `Start`, `Step`, `Finish`, private `gsasl_new`, `init_kerberos`, and raw GSASL context/session pointers.

Control flow: same base SASL lifecycle: configure credentials/mechanism, start, step through server challenges, then finish.

State and persistence: per-engine GSASL context/session pointers and inherited optional credential/mechanism state. No persistent storage.

Dependencies and integration: includes `<gsasl.h>` and base `sasl_engine.h`; selected through CMake when `CMAKE_USING_GSASL` is enabled.

Risks and test signals: raw pointer ownership and cleanup need partial-init tests. Header exposes no copy prevention, so accidental copying would duplicate raw pointer ownership if generated by compiler; usage should avoid copying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/gsasl_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/namenode_tracker.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/namenode_tracker.cc

Purpose: implements HA NameNode tracking for failover decisions inside `RpcEngine`.

Important APIs and functions: constructor, destructor, `GetFailoverAndUpdate`, `IsCurrentActive_locked`, `IsCurrentStandby_locked`, and helper `format_endpoints`.

Control flow: the constructor enables HA when at least two resolved NameNode infos are available, stores first as active candidate and second as standby candidate, and marks resolved if endpoints exist. `GetFailoverAndUpdate` identifies whether the current endpoint belongs to active or standby, swaps active/standby on active failure, emits events, and optionally re-resolves endpoints for the selected node.

State and persistence: in-memory active/standby `ResolvedNamenodeInfo`, booleans `enabled_`/`resolved_`, `IoService`, event handlers, and `swap_lock_`. No disk persistence; “active” is a client-side current guess.

Dependencies and integration: depends on NameNode resolution helpers, event handlers, logging, Boost TCP endpoints, and `IoService`. Used by `RpcEngine::RpcCommsError` when retry policy requests failover.

Risks and test signals: only the first two NameNodes are used even if more are configured. Endpoint comparison ignores port mismatch after logging, matching only address. Failover event context uses a cast of `c_str()` to integer, which is fragile for consumers. Tests should cover active failure, standby response, empty endpoint vectors, unresolved standby, and DNS re-resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/namenode_tracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/namenode_tracker.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/namenode_tracker.h

Purpose: declares `HANamenodeTracker`, a helper that maps a failed endpoint to an alternate HA NameNode.

Important APIs and types: constructor, destructor, `is_enabled`, `is_resolved`, `GetFailoverAndUpdate`, private active/standby endpoint checks, active/standby `ResolvedNamenodeInfo`, and `swap_lock_`.

Control flow: `RpcEngine` owns the tracker when HA config is detected and asks it for alternate endpoints on failover retries. The call mutates internal active/standby state.

State and persistence: in-memory enabled/resolved flags, `IoService`, event handlers, active/standby info, and mutex. No persistent state across process restarts.

Dependencies and integration: includes event and NameNode info helpers plus Boost endpoints. This is part of RPC retry/failover integration.

Risks and test signals: public `GetFailoverAndUpdate` always mutates state; callers needing read-only checks cannot use it safely. Tests should validate locking and behavior with more than two configured NameNodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/namenode_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/request.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/request.cc

Purpose: implements RPC request packet construction and response callback dispatch.

Important APIs and functions: protobuf helpers `AddHeadersToPacket`, `ConstructPayload`, `SetRequestHeader`; `Request` constructors; `GetPacket`; `OnResponseArrived`; `GetDebugString`; `IncrementFailoverCount`.

Control flow: normal requests serialize the protobuf payload at construction. `GetPacket` builds an RPC request header and method header, then writes length-prefixed delimited protobuf headers plus payload. SASL requests omit the method request header. Null requests represent connection tracking and generate no payload, causing immediate callback completion in the connection layer.

State and persistence: stores weak engine, method name, call id, deadline timer, serialized payload, handler, retry count, and failover count. State is per request and in-memory only.

Dependencies and integration: depends on Hadoop RPC header protobufs, `RpcEngine` lock-free metadata, `SaslProtocol` method name, protobuf coded streams, and `IoService` timers. Used by `RpcConnection` queues and retry logic.

Risks and test signals: if `client_id()` generation failed, header construction logs and returns with a partly initialized header. Retry count is reset on failover via `IncrementFailoverCount`. Tests should validate packet bytes for normal, SASL, and null requests; retry/failover counters; and timer cancellation on response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/request.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/request.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/request.h

Purpose: declares `Request`, internal bookkeeping for an outstanding NameNode RPC.

Important APIs and types: `Handler`, normal and null constructors, `call_id`, `method_name`, `timer`, `IncrementRetryCount`, `IncrementFailoverCount`, `GetPacket`, `OnResponseArrived`, `get_failover_count`, and `GetDebugString`.

Control flow: `RpcConnection` constructs requests, queues them, asks for serialized packets, starts request timers, and invokes `OnResponseArrived` after parsing a response or error.

State and persistence: weak engine pointer, method name, call id, Boost deadline timer, payload string, response handler, retry count, and failover count. Not thread-safe and intended to be accessed by one connection/engine path at a time.

Dependencies and integration: depends on status, utilities, protobuf message/coded-stream APIs, and Boost deadline timers. It is central to retry and response correlation.

Risks and test signals: weak engine access can fail during filesystem destruction, producing errors instead of packets. Tests should cover request lifetime during shutdown, no-retry policy initialization, and not-thread-safe assumptions under connection locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection.h

Purpose: declares the `RpcConnection` abstraction for a persistent NameNode connection with multiplexed in-flight RPCs and ordered response handling.

Important APIs and types: connection lifecycle methods `Connect`, `ConnectAndFlush`, `Disconnect`, handshake/context methods, send/receive completion hooks, `FlushPendingRequests`, `AsyncRpc`, request enqueue helpers, event/auth setters, timeout/error handling, and response state structures/queues.

Control flow: concrete implementations connect sockets, send handshake and context, queue requests, write packets one at a time, read length-prefixed responses, match by call id, and return communication errors to `RpcEngine` for retry.

State and persistence: connection state enum, weak engine pointer, auth info, SASL protocol, pending/auth/sent request queues, outgoing request, current response parser state, event handlers, cluster name, and `connection_state_lock_`. No disk persistence.

Dependencies and integration: depends on `Request`, auth info, event handlers, status, Boost TCP/system types, protobuf response parsing in implementation, and `LockFreeRpcEngine`.

Risks and test signals: lock ordering is documented: engine lock before connection lock, and callbacks must not run while holding locks. Tests should cover concurrent RPC enqueue, unknown call ids, disconnect while pending, timeout removal, and callbacks posted outside locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection_impl.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection_impl.cc

Purpose: implements non-template `RpcConnection` logic: handshake/auth/context progression, response parsing, request creation/queueing, packet construction for handshake/context, comms error handling, timeouts, and event hooks.

Important APIs and functions: `AddHeadersToPacket`, constructor/destructor, `GetIoService`, `StartReading`, `HandshakeComplete`, `AuthComplete`, `AuthComplete_locked`, `ContextComplete`, `AsyncFlushPendingRequests`, `HandleRpcResponse`, `HandleRpcTimeout`, `PrepareHandshakePacket`, `PrepareContextPacket`, `AsyncRpc`, `AsyncRpc_locked`, `SendRpcRequests`, `PreEnqueueRequests`, `PrependRequests_locked`, setters, `CommsError`, `ClearAndDisconnect`, `RemoveFromRunningQueue`, and `ToString`.

Control flow: after socket-level handshake succeeds, connection enters authenticating. If SASL is required and compiled, `SaslProtocol::Authenticate` runs; otherwise unsecured auth completes. Context packet is sent, state becomes connected, and pending requests flush. Responses are parsed into `RpcResponseHeaderProto`, matched to sent requests, and callbacks are posted on the `IoService`. Standby exceptions prepend the request and trigger comms error for failover.

State and persistence: manipulates in-memory queues, current response buffers, connection state, auth info, SASL protocol object, and timers. No disk persistence.

Dependencies and integration: depends on Hadoop RPC/context protobufs, `RpcEngine`, `SaslProtocol`, protobuf coded streams, Boost ASIO, and event injection hooks. Template socket operations live in `rpc_connection_impl.h`.

Risks and test signals: `PrepareContextPacket` sets RPC header client id from `client_name` rather than `client_id`, which should be verified against protocol expectations. `HandleRpcTimeout` calls request callback while holding the connection lock, unlike the no-lock callback rule. Standby exception retry prepends a request and calls `CommsError`; tests should cover failover and duplicate response races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection_impl.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection_impl.h

Purpose: defines the template `RpcConnectionImpl<Socket>` for concrete Boost ASIO socket I/O.

Important APIs and functions: constructor/destructor, `Connect`, `ConnectAndFlush`, `ConnectComplete`, `SendHandshake`, `SendContext`, `OnSendCompleted`, `FlushPendingRequests`, `OnRecvCompleted`, and `Disconnect`.

Control flow: `ConnectAndFlush` selects an endpoint, starts async connect, and arms a connect timeout. `ConnectComplete` cancels the timer, tries additional endpoints on failure, or starts reading and sends handshake on success. `FlushPendingRequests` chooses auth or normal queues depending on state, serializes a request, starts its timeout, and writes it. `OnRecvCompleted` drives a three-stage read state: length, content, parse response.

State and persistence: stores options, current/additional endpoints, socket, connect timer, inherited queues/state, and auth/event data. Runtime only.

Dependencies and integration: depends on Boost ASIO sockets/timers/read/write, `RpcConnection`, `RpcEngine`, `Request`, auth info, logging, utility socket disconnect helpers, and `IoService`.

Risks and test signals: connect timer handler calls `ConnectComplete` with host-unreachable when not canceled, so old async operations must be ignored by endpoint/state checks. `FlushPendingRequests` assumes connection lock is held and uses request timers with weak connection/request captures. Tests should cover endpoint fallback, connect timeout, write/read errors, empty payload null requests, and operation-aborted reads during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_connection_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_engine.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_engine.cc

Purpose: implements `RpcEngine`, the reliable NameNode RPC coordinator handling connection creation, retry policy selection, HA failover, request resubmission, client IDs, and event hooks.

Important APIs and functions: constructor, `Connect`, `CancelPendingConnect`, `Shutdown`, `MakeRetryPolicy`, `getRandomClientId`, test setters, `AsyncRpc`, `NewConnection`, `InitializeConnection`, `AsyncRpcCommsError`, `RpcCommsError`, and `SetFsEventCallback`.

Control flow: `Connect` records endpoints/cluster, creates HA tracker if applicable, builds retry policy, initializes a connection, and connects. `AsyncRpc` checks cancellation, recreates a connection if needed, and forwards to it. `RpcCommsError` filters failed requests through retry policy, posts final failures, optionally obtains alternate HA endpoints, creates a new connection, pre-enqueues retry requests, and connects immediately or after delay.

State and persistence: in-memory `io_service_`, options, client name/id, protocol/user/auth info, retry policy, cluster name, atomic call id, retry timer, event handlers, engine lock, cancellation flag, last endpoints, and optional HA tracker. No disk persistence.

Dependencies and integration: depends on `RpcConnectionImpl`, retry policies, auth info, NameNode info, OpenSSL random APIs, Boost timers, and event hooks. Called by generated HRPC stubs through `NameNodeOperations`.

Risks and test signals: `Connect` assumes `servers[0]` exists. `CancelPendingConnect` only flips a flag; lower-level cancellation is cooperative via later checks. Retry/failover mutates request retry/failover counts and endpoint state. Tests should cover no endpoints, random client ID failure, canceled connect followed by RPC, fixed-delay retry, HA failover, and event-injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_engine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_engine.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_engine.h

Purpose: declares `RpcEngine` and `LockFreeRpcEngine`, the central thread-safe RPC coordinator and the restricted interface connections can call while holding their own locks.

Important APIs and types: RPC version/call-id constants, `Connect`, `CancelPendingConnect`, `AsyncRpc`, `Shutdown`, `AsyncRpcCommsError`, `RpcCommsError`, retry/client/protocol accessors, test hooks, `SetFsEventCallback`, connection factory methods, and HA endpoint state.

Control flow: generated stubs call `AsyncRpc`; connections call lock-free metadata and comms-error callbacks; engine owns retry/failover decisions and connection replacement.

State and persistence: shared current connection, `IoService`, options, client identity, protocol metadata, retry policy, auth info, cluster name, atomic call ID, retry timer, event handlers, engine mutex, cancellation flag, last endpoints, and optional HA tracker. Runtime only.

Dependencies and integration: includes options/status, auth/retry/event/util helpers, NameNode tracker, protobuf message lite, Boost TCP/timer, atomics/mutexes. It integrates filesystem NameNode operations with transport-level RPC.

Risks and test signals: the header’s lock-order note is a key correctness contract. Tests and reviews should check that new code does not call engine-locking methods from connection-locked paths and that callbacks are not invoked under internal locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/rpc_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_engine.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_engine.cc

Purpose: implements base `SaslEngine` credential setters, state accessor, destructor, and mechanism selection.

Important APIs and functions: `GetState`, destructor, `SetKerberosInfo`, `SetPasswordInfo`, and `ChooseMech`.

Control flow: callers set credentials while unstarted, then pass available server mechanisms to `ChooseMech`. The implementation currently accepts only `GSSAPI`, deep-copies the chosen method, and returns true. If none match, it sets error state and clears `chosen_mech_`.

State and persistence: inherited state includes current state and optional principal/realm/id/password plus chosen mechanism. No disk persistence.

Dependencies and integration: depends on base header and logging/status indirectly. Used by Cyrus and GSASL implementations and by SASL protocol negotiation.

Risks and test signals: `ChooseMech` returns `auth.mechanism.c_str()` as a bool, which works as non-null true but is semantically odd. Only GSSAPI is supported despite password setters. Tests should cover empty mechanism lists, non-GSSAPI choices, and deep-copy lifetime after input vector destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_engine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_engine.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_engine.h

Purpose: declares the abstract SASL engine interface and common mechanism/credential state.

Important APIs and types: `SaslMethod`, `SaslEngine::State`, `SetKerberosInfo`, `SetPasswordInfo`, `ChooseMech`, `GetState`, abstract `Start`, `Step`, `Finish`, and public `chosen_mech_`.

Control flow: expected lifecycle is unstarted, start to waiting-for-data, repeated step to success/failure, then finish. Concrete backends implement token exchange with Cyrus or GSASL.

State and persistence: state enum, optional principal/realm/id/password, raw `SaslProtocol *`, and chosen mechanism. No persistent state.

Dependencies and integration: depends on libhdfspp `Status` and optional wrapper. Used by `SaslProtocol` and backend engines selected at build time.

Risks and test signals: comments duplicate the transition diagram. `chosen_mech_` is public mutable state, and no copy prevention exists in base class. Tests should verify backend implementations respect state preconditions and cleanup even after failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/sasl_engine.h -->
