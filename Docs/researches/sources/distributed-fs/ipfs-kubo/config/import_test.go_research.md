# Research: sources/distributed-fs/ipfs-kubo/config/import_test.go

Purpose: Broad unit coverage for import configuration validation and derived UnixFS behavior.

Important APIs/types/functions: Tests cover `ValidateImportConfig` for HAMT fanout, CID version, file/directory max links, batch limits, chunkers, hash functions, defaults, HAMT size estimation, and DAG layout. It also tests `isValidChunker`, `isPowerOfTwo`, `UnixFSCidBuilder`, default CID builder behavior, and `HAMTSizeEstimationMode`.

Control flow, state, and persistence: Pure in-memory table tests. CID builder tests generate CIDs from `[]byte("test")` to inspect prefix version and multihash type.

Dependencies and integration points: Uses Boxo UnixFS size-estimation constants and multihash names. It protects config behavior consumed by `ipfs add` and MFS import.

Risks and test signals: Coverage is strong for validation edges and import defaults. It does not run full UnixFS imports, so actual DAG layout, batch writing, and chunk output compatibility are covered elsewhere.
