# sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe-global.h

## Purpose
`lmdb-safe-global.h` provides the symbol import/export macros used by the vendored `lmdb-safe` C++ wrapper. In this POSIX RGW driver tree it controls whether `LMDB_SAFE_EXPORT` and `LMDB_SAFE_IMPORT` resolve to cpp-utilities visibility attributes or to empty definitions for static/no-utilities builds.

## Important APIs, Types, and Functions
The only public API is preprocessor-level: `LMDB_SAFE_EXPORT` and `LMDB_SAFE_IMPORT`. If `LMDB_SAFE_NO_CPP_UTILITIES` is not defined, the header includes `<c++utilities/application/global.h>` and maps the macros to `CPP_UTILITIES_GENERIC_LIB_EXPORT` and `CPP_UTILITIES_GENERIC_LIB_IMPORT` unless `LMDB_SAFE_STATIC` is defined. If cpp-utilities is disabled, the header forces `LMDB_SAFE_STATIC` and makes both macros empty.

## Control Flow
There is no runtime control flow. Compile-time flow chooses between dynamic-library visibility and static/no-op visibility based on `LMDB_SAFE_NO_CPP_UTILITIES` and `LMDB_SAFE_STATIC`.

## State and Persistence Behavior
The header owns no state and has no persistence behavior. Its impact is ABI/linkage visibility for classes declared in `lmdb-safe.hh`, such as `LMDBError`, `MDBEnv`, transaction wrappers, and cursors.

## Dependencies and Integration Points
It is included by `lmdb-safe.hh`. When cpp-utilities is available, it depends on that project's generic library visibility macros. The POSIX RGW cache includes `lmdb-safe.hh`, so any build-system mismatch here affects bucket listing cache compilation/linkage.

## Risks
The most likely risk is build portability. A dynamic build without cpp-utilities must define `LMDB_SAFE_NO_CPP_UTILITIES`, otherwise the include will fail. Conversely, incorrect `LMDB_SAFE_STATIC` settings can hide symbols needed by a shared library. The include guard uses `LMDB_SAFE_GLOBAL`, which is simple but could collide with another macro in a broad build.

## Test Signals
Compile the POSIX RGW driver in both static and shared configurations, with and without cpp-utilities visibility macros. Link tests should instantiate exported `LMDBSafe` classes from another translation unit.
