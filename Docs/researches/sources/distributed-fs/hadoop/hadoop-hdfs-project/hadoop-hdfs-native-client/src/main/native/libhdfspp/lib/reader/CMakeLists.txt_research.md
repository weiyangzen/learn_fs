# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/CMakeLists.txt

Purpose: defines the libhdfspp reader build target for DataNode block reading and data-transfer helpers.

Important APIs and targets: `reader_obj` object library built from `block_reader.cc`, `datatransfer.cc`, and `readergroup.cc`; dependency on `proto`; final `reader` library from object files.

Control flow: CMake compiles reader sources after generated protobuf artifacts are available, then exposes them through a static/object-composed `reader` library.

State and persistence: build metadata only; no runtime state.

Dependencies and integration: depends on the `proto` target because reader code uses `datatransfer.pb.h` and HDFS block protobufs. The library integrates with file handles and DataNode connections elsewhere in libhdfspp.

Risks and test signals: build tests should ensure `proto` generation completes before reader compilation and optional platform/link settings from parent CMake files remain sufficient for Boost ASIO/protobuf use.
