# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/fileinfo.h

Purpose: defines internal file block-location metadata used by file handles and readers after NameNode lookup.

Important APIs and types: `struct FileInfo` with `file_length_`, `last_block_complete_`, `under_construction_`, and `std::vector<LocatedBlockProto> blocks_`.

Control flow: `NameNodeOperations::GetBlockLocations` populates this structure; `FileSystemImpl::Open` passes it to `FileHandleImpl`; block readers consume located block data to contact DataNodes.

State and persistence: plain in-memory aggregate with protobuf block copies. No methods and no disk persistence.

Dependencies and integration: depends on `hdfs.pb.h` for `LocatedBlockProto`. Bridges NameNode metadata and reader/file-handle code.

Risks and test signals: correctness depends on NameNode conversion logic, especially incomplete last-block handling and file length adjustment. Tests should verify empty files, under-construction files, and multi-block files.
