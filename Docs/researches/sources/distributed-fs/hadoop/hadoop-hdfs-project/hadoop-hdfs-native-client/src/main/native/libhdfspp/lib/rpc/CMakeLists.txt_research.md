# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/CMakeLists.txt

Purpose: defines the RPC library build target and conditionally includes SASL backend implementations.

Important APIs and targets: `rpc_object_items`, conditional appends for `cyrus_sasl_engine.cc` and `gsasl_engine.cc`, object library `rpc_obj`, dependency on `proto`, final library `rpc`, include directories, and Boost linkage.

Control flow: CMake collects common RPC sources plus x-platform objects, conditionally appends SASL sources based on configuration flags, builds object files after protobuf generation, and exposes the `rpc` library.

State and persistence: build configuration only.

Dependencies and integration: depends on `proto`, Boost libraries, local include paths, and optional Cyrus/GSASL availability. This build target feeds NameNode RPC functionality used by filesystem operations.

Risks and test signals: SASL compile paths depend on CMake flags and external libraries; CI should cover unsecured, Cyrus SASL, and GSASL builds where supported. Missing `sasl_protocol.cc` from this work item is still included in the build target, so link/test failures may arise outside this subset.
