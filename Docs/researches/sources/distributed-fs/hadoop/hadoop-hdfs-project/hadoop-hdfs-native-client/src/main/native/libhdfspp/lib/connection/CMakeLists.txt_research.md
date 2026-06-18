<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/CMakeLists.txt

## Purpose
Defines the build target for the libhdfspp DataNode connection layer.

## Important APIs, Types, And Functions
The file creates `connection_obj` from `datanodeconnection.cc`, adds a dependency on generated protobuf target `proto`, and creates the `connection` library from the object target.

## Control Flow
CMake ensures protobuf classes are generated before compiling DataNode connection code that includes `ClientNamenodeProtocol.pb.h`.

## State And Persistence
No runtime state exists.

## Dependencies And Integration Points
Connects the connection module to generated protobufs and higher-level fs/reader libraries.

## Risks
If new connection sources are added but omitted here, link errors or missing behavior will result. The target does not declare include dirs locally, so it relies on parent/global include configuration.

## Test Signals
Signals are successful CMake generation, protobuf dependency ordering, and link of consumers using `DataNodeConnectionImpl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/CMakeLists.txt -->
