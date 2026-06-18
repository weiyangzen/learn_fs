# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/c/CMakeLists.txt

## Purpose
This CMake file builds the libhdfs++ C binding object library and a standalone binding library target.

## Important APIs, Control Flow, and State
It creates `bindings_c_obj` as an object library from x-platform object files and `hdfs.cc`, then declares dependencies on `fs`, `rpc`, `reader`, `proto`, `common`, and `x_platform_obj`. It also creates `bindings_c` from `bindings_c_obj` and `x_platform_obj`.

## Dependencies and Integration Points
The top-level libhdfs++ library aggregates `bindings_c_obj` into `LIBHDFSPP_ALL_OBJECTS`, making C ABI functions part of the main library. C examples link the static library and include `hdfs_ext.h`.

## Risks and Test Signals
Object-library reuse can duplicate symbols if aggregate targets also include the same x-platform objects independently. The dependency list repeats several targets. Tests should link static and shared libraries, inspect exported C symbols, and build C examples to validate no missing or duplicate objects.
