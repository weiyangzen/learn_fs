# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/CMakeLists.txt

## Purpose
Builds the SQLite DB backend static library for the older dbstore operation layer.

## APIs, Flow, And State
The CMake file requires SQLite3, sets `sqliteDB.h` and `sqliteDB.cc` as `sqlite_db` sources, defines `SQLITE_THREADSAFE=1` through global C++ flags, builds `sqlite_db` as a static library, and links it against `sqlite3`, `dbstore_lib`, and `rgw_common`.

## Dependencies And Integration
Depends on CMake 3.14, `find_package(SQLite3 REQUIRED)`, Ceph build helpers such as `COMPILER_SUPPORTS_VLA_ERROR`, and parent build wiring that enables the dbstore/sqlite subdirectory.

## Risks And Test Signals
Only `sqliteDB.*` is included here; the config-store SQLite wrapper files are built elsewhere. The use of global `CMAKE_CXX_FLAGS` is broader than target-local compile definitions. Build signal is successful `sqlite_db` compilation/linking and unit tests that link the dbstore target.
