<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/CMakeLists.txt

## Purpose
Defines the build target for the libhdfspp filesystem layer.

## Important APIs, Types, And Functions
The file builds `fs_obj` from `filesystem.cc`, `filesystem_sync.cc`, `filehandle.cc`, `bad_datanode_tracker.cc`, and `namenode_operations.cc`, includes x-platform objects, adds private include path `../lib`, depends on `proto`, and creates the `fs` library.

## Control Flow
CMake ensures generated protobufs exist before compiling filesystem sources and packages object files for higher-level library links.

## State And Persistence
No runtime state exists.

## Dependencies And Integration Points
This target integrates filesystem operations, synchronous wrappers, file handles, bad DataNode tracking, namenode operation glue, x-platform helpers, and protobuf-generated protocol classes.

## Risks
New fs sources must be added here. The relative include path is sensitive to source-tree layout. Object-library reuse can hide missing transitive link dependencies until final link.

## Test Signals
Signals are successful build ordering, complete fs symbol linkage, and filesystem/open/read tests against a mini cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/CMakeLists.txt -->
