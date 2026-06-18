# Research: sources/distributed-fs/ipfs-kubo/config/import.go

Purpose: Defines import defaults and validation for UnixFS ingestion behavior used by `ipfs add`, MFS writes, DAG/block import paths, and related commands.

Important APIs/types/functions: `Import` stores CID version, raw leaves, chunker, hash, max links, HAMT fanout/threshold/estimation, DAG layout, batch limits, and fast-provide flags. `ValidateImportConfig`, `isPowerOfTwo`, `isValidChunker`, `HAMTSizeEstimationMode`, `UnixFSSplitterFunc`, `MFSRootOptions`, and `UnixFSCidBuilder` are the core functions.

Control flow, state, and persistence: Validation only checks explicitly configured optional values. It restricts CID version to 0/1, positive file links and batch limits, non-negative directory max links, HAMT fanout power-of-two from 8 through 1024, recognized/allowed hash functions, valid chunker syntax, valid HAMT estimation modes, and valid DAG layouts. `UnixFSSplitterFunc` returns an optimized size splitter when possible and falls back to Boxo parsing/default splitter for invalid rare cases. `UnixFSCidBuilder` upgrades CIDv0 to CIDv1 when using non-default hash and always returns an explicit prefix. Values persist in config and alter resulting CIDs.

Dependencies and integration points: Uses Boxo chunker, UnixFS helpers, MFS, verifcid, go-cid, and multihash. `core/commands/add.go`, MFS, and profiles use these defaults.

Risks and test signals: Import settings directly affect CID determinism and interoperability. `UnixFSSplitterFunc` can silently fall back if invalid config bypasses validation. `import_test.go` extensively covers validation, chunkers, CID builders, defaults, HAMT estimation, and DAG layout.
