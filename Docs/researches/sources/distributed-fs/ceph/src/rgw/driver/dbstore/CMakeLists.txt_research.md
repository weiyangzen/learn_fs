<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/CMakeLists.txt

## Purpose
This CMake file builds the RGW DBStore backend library, optional SQLite support, DBStore manager library, tests, and a small standalone `dbstore-bin` executable. It defines the common source set, links the RGW dependencies, and wires the SQLite backend into the build when `USE_SQLITE` is enabled.

## Important APIs, Types, And Functions
- `option(USE_SQLITE "Enable SQLITE DB" ON)` controls whether SQLite implementation files and the `sqlite` subdirectory are included.
- `dbstore_srcs` contains common backend logic (`common/dbstore_log.h`, `common/dbstore.h`, `common/dbstore.cc`) plus `config/store.cc`; SQLite mode appends `config/sqlite.cc`, `sqlite/connection.cc`, `sqlite/error.cc`, and `sqlite/statement.cc`.
- `dbstore_lib` is the library for common DBStore implementation and backend-specific SQLite pieces.
- `dbstore` is a static library built from `dbstore_mgr.h` and `dbstore_mgr.cc`, linked against `dbstore_lib`, RGW common code, optional SQLite library, pthread, and optional Jaeger support.
- `dbstore-bin` is a testing executable built from `dbstore_main.cc`.
- `WITH_TESTS` gates `add_subdirectory(tests)`; otherwise it emits a warning that GTest is not enabled.

## Control Flow
CMake config starts by defining include paths and common source lists. If SQLite is enabled, SQLite sources are appended to `dbstore_srcs`, the `sqlite` subdirectory is added, `SQLITE_ENABLED=1` is defined, and `sqlite_db` is linked and ordered after `dbstore_lib`. `dbstore_lib` is created first and linked to Boost context, optional `jaeger_base`, and `rgw_common`. The manager static library `dbstore` is then created and linked to the accumulated `CMAKE_LINK_LIBRARIES`. Finally, `dbstore-bin` is created and linked for testing.

## State And Persistence
The build file itself has no runtime persistence, but it determines which DBStore persistence backend exists in the binary. With `USE_SQLITE=ON`, SQLite connection, statement, and error handling are compiled, and table-backed persistence paths in `dbstore.h`/`dbstore.cc` can be exercised. It also creates static/shared build artifacts and test binaries in the build tree.

## Dependencies And Integration Points
The file depends on the surrounding Ceph CMake environment, `Boost::context`, `rgw_common`, optional `jaeger_base`, optional GTest through `WITH_TESTS`, pthread, and the local `sqlite` subdirectory. Include directories expose `${CMAKE_SOURCE_DIR}/src/rgw`, `${CMAKE_SOURCE_DIR}/src/rgw/store/rados`, and the current DBStore source directory to consumers.

## Risks And Edge Cases
- It mutates global `CMAKE_INCLUDE_DIR` and `CMAKE_LINK_LIBRARIES`, which can make link/include behavior order-dependent and harder to reason about than target-local properties.
- `dbstore_lib` includes header files as sources; this is harmless for IDE visibility but can obscure which files actually compile.
- `dbstore` is static while `dbstore_lib` uses default library type; mixed library type expectations can vary by parent CMake settings.
- `USE_SQLITE=OFF` leaves `dbstore_lib` without SQLite implementation files, so code paths that assume `SQLITE_ENABLED` or `sqlite_db` need compile guards.
- The file calls `find_package(gtest QUIET)` but uses `WITH_TESTS` rather than the package result to decide whether to add tests.
- `add_dependencies(sqlite_db dbstore_lib)` assumes the `sqlite` subdirectory creates a `sqlite_db` target.

## Test Signals
Build `dbstore_lib`, `dbstore`, and `dbstore-bin` with `USE_SQLITE=ON` and `OFF`. Run CMake with `WITH_TESTS=ON` to ensure the `tests` subdirectory compiles and links. Verify `-Werror=vla` coverage when `COMPILER_SUPPORTS_VLA_ERROR` is set. Link failures around `sqlite_db`, `rgw_common`, or `Boost::context` are the main integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/CMakeLists.txt -->
