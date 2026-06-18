# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileMDSvcTest.cc

Purpose: Integration tests for QuarkDB-backed file metadata service and tree accounting helper arithmetic.
Important APIs/types/functions: `FileMDSvcF`, `fileSvc()->createFile/updateStore/removeFile/getFileMD/getFileMDFut`, `mdFlusher()->synchronize`, and `TreeInfos` operators.
Control flow: `LoadTest` creates five files, persists them, removes two, finalizes/reinitializes, restarts services, verifies surviving and deleted IDs, checks multiple futures for one fid point to the same in-memory object, then removes remaining files. `TreeInfos` checks zero/negation/addition behavior.
State/persistence: validates QDB file count, object names, deletion persistence, and cache/future state after reload.
Dependencies/integration: uses constants, file/container services, hierarchical view, test fixture, and private access to `FileSystemView` for testing.
Risks: relies on allocator starting from known IDs through fixture flush; future coalescing assertion is pointer-identity based and could be invalidated by intentional cache design changes.
Test signals: strong for file CRUD, persistence across restart, missing-ID exceptions, future deduplication, and basic accounting arithmetic.
