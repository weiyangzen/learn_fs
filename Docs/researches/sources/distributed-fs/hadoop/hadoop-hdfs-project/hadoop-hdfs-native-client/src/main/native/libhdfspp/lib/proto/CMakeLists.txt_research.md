# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/proto/CMakeLists.txt

Purpose: defines protobuf and generated-HRPC build steps for libhdfspp. It generates C++ protobuf sources from Hadoop/HDFS `.proto` files, builds the custom `protoc-gen-hrpc` plugin, and creates the `proto` library.

Important APIs and functions: `protobuf_generate_cpp`, executable target `protoc-gen-hrpc`, custom CMake function `GEN_HRPC`, `gen_hrpc(HRPC_SRCS ClientNamenodeProtocol.proto)`, object library `proto_obj`, and final library `proto`.

Control flow: CMake builds protobuf outputs for many Hadoop protocol files, builds the HRPC plugin, then `GEN_HRPC` invokes `protoc` with `--plugin=protoc-gen-hrpc` and `--hrpc_out` to produce `.hrpc.inl` stubs in the binary directory.

State and persistence: generated build artifacts live under `CMAKE_CURRENT_BINARY_DIR`; no runtime state. The function appends include paths from `PROTOBUF_IMPORT_DIRS` while avoiding duplicates.

Dependencies and integration: depends on protobuf compiler/library targets, Hadoop proto directories, optional `copy_hadoop_files`, and `${protobuf_ABSL_USED_TARGETS}`. Downstream `fs` and `rpc` code depends on generated protobuf and HRPC files.

Risks and test signals: duplicate `datatransfer.proto` appears in the generation list and may be benign or build-system-sensitive. Build tests should verify clean builds, incremental regeneration when proto/plugin changes, and generated include visibility for `ClientNamenodeProtocol.hrpc.inl`.
