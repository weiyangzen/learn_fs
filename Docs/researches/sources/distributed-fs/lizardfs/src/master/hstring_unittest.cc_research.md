# sources/distributed-fs/lizardfs/src/master/hstring_unittest.cc

Purpose: tests `HString` and `hstorage::Handle` behavior for memory storage and, when compiled in, Berkeley DB storage.

Important APIs/types/functions: `Name` checks backend name; `MemComparison`, `MemGet`, `MemHash`, and `MemCopy` cover comparison, retrieval, hash extraction, copy/move assignment for `MemStorage`; BDB variants repeat comparison/get/hash/copy behavior with a temporary DB file.

Control flow: each test installs a storage backend with `Storage::reset()`, creates `HString` and `Handle` objects, performs comparisons or assignments, and resets/removes BDB files after handles leave scope.

State and persistence behavior: tests manipulate the process-global storage singleton and temporary `/tmp/db.db` for BDB.

Dependencies/integration: depends on GoogleTest, `MemStorage`, optional `BDBStorage`, and standard functional utilities.

Risks and test signals: BDB copy test appears to install `MemStorage`, so it does not actually exercise BDB copy semantics. Tests use a fixed `/tmp/db.db` path, which can collide across parallel runs. They do not cover move assignment over an already-bound destination.
