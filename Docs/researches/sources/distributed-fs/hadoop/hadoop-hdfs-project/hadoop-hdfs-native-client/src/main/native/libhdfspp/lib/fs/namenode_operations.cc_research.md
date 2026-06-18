# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/namenode_operations.cc

Purpose: implements `NameNodeOperations`, the translation layer between filesystem calls and `ClientNamenodeProtocol` protobuf RPCs. It builds request protobufs, dispatches generated RPC stub methods, and converts response protobufs into libhdfspp public data structures and statuses.

Important APIs and functions: `Connect`, `CancelPendingConnect`, `GetBlockLocations`, `GetPreferredBlockSize`, `SetReplication`, `SetTimes`, `GetFileInfo`, `GetContentSummary`, `GetFsStats`, `GetListing`, `Mkdirs`, `Delete`, `Rename`, `SetPermission`, `SetOwner`, snapshot operations, `SetFsEventCallback`, and conversion helpers for file status, content summary, directory listing, and fs stats.

Control flow: each operation validates required path/argument values, populates the corresponding Hadoop protobuf request, allocates a shared response, invokes `namenode_.Method`, and in the callback maps server response fields into libhdfspp objects. Boolean result methods translate successful RPCs with false/missing result into `PathNotFound` or `InvalidArgument` because NameNode responses may not include detailed reasons.

State and persistence: holds only in-memory RPC engine/stub state inherited from the header. Request/response protobufs are per-call objects captured by callbacks. No disk persistence.

Dependencies and integration: depends on generated Hadoop HDFS protobuf classes and generated `.hrpc.inl` stubs. It sits below `FileSystemImpl` and above `RpcEngine`, so changes here affect all filesystem metadata and namespace operations.

Risks and test signals: “OK but missing field” behavior is deliberately normalized and should be covered for nonexistent files/directories. `GetBlockLocations` appends an incomplete last block when present, affecting file length and read planning. Directory listing path composition appends `/`, so root and child path edge cases need tests. High-bit checks prevent protobuf negative-value errors for uint64 offsets/lengths.
