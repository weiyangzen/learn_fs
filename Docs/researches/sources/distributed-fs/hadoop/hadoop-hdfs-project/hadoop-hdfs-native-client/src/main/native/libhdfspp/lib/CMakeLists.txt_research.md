# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/CMakeLists.txt

## Purpose
This CMake file defines the libhdfs++ implementation submodule graph.

## Important APIs, Control Flow, and State
It adds subdirectories for `x-platform`, `common`, `fs`, `reader`, `rpc`, `proto`, `connection`, and `bindings`. There is no runtime state; it controls build ordering and target discovery.

## Dependencies and Integration Points
The top-level CMake file later aggregates object libraries from these subdirectories into `hdfspp_static` and `hdfspp`. The bindings directory includes the C binding object target.

## Risks and Test Signals
Removing or reordering subdirectories can break object target availability. Configure tests should verify all expected object libraries are defined and aggregate targets include them exactly once.
