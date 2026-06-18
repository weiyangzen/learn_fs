<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/lmdb/midl.h -->
# sources/distributed-fs/orangefs/src/common/lmdb/midl.h

Purpose: declares LMDB's internal ID-list types and helper APIs. The header explicitly says these definitions are internal to `libmdb` and not public LMDB API. It documents the key representation contracts used by `midl.c`.

Important types and macros: `MDB_ID` is a `size_t`; `MDB_IDL` is a pointer to an array whose element zero is a count and whose allocated length is stored one element before the exposed pointer (`MDB_IDL_ALLOCLEN(ids)`). `MDB_IDL_LOGN`, `MDB_IDL_DB_SIZE`, `MDB_IDL_UM_SIZE`, and max macros define normal and upper IDL capacities. `MDB_IDL_SIZEOF`, `MDB_IDL_IS_ZERO`, `MDB_IDL_CPY`, `MDB_IDL_FIRST`, `MDB_IDL_LAST`, and `mdb_midl_xappend()` provide fast, mostly unchecked operations. `MDB_ID2` pairs an ID with a pointer, and `MDB_ID2L` uses `ids[0].mid` as its count.

Public internal API declarations include search, allocation/free, shrink, capacity reservation, append, range append, merge, sort, and ID2L search/insert/append. The integration point is `mdb.c`, plus the build fragment that compiles `midl.c` with the embedded LMDB source.

State behavior is entirely in-memory: the header defines how callers must shape arrays and when they may use unchecked macros. No locking is provided; concurrency is the caller's responsibility. Risks center on representation misuse, unchecked macro append, and the fact that IDLs and ID2Ls sort in opposite directions. Test signals should assert count/allocation invariants, macro behavior with pre-sized arrays, C++ inclusion via `extern "C"`, and compatibility with pointer-sized IDs across 32-bit and 64-bit targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/lmdb/midl.h -->
