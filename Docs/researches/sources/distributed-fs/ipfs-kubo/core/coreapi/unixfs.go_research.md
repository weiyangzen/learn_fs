# sources/distributed-fs/ipfs-kubo/core/coreapi/unixfs.go

Purpose: implements CoreAPI UnixFS add/get/list operations.

Important APIs/types/functions: `UnixfsAPI` methods `Add`, `Get`, `Ls`, helper methods `processLink`, `lsFromDirLinks`, `lsFromLinks`, `core`, and `syncDagService`.

Control flow: `Add` parses many UnixFS add options, reads repo config, validates `--nocopy` against filestore/urlstore enablement, selects a blockstore/exchange/pinner strategy for normal, cache/nocopy, or only-hash mode, builds a blockservice/DAG service wrapped in `syncDagService`, configures a `coreunix.Adder` with chunker/layout/CID/raw leaf/pin/metadata/HAMT options, optionally wraps CID builder for inline CIDs, creates a mock MFS root for only-hash, and calls `AddAllAndPin`. `Get` resolves a node through a read-only session and returns a UnixFS file. `Ls` resolves a node, treats directories via `uio.Directory`, otherwise lists raw links; `processLink` resolves child metadata when requested.

State and persistence behavior: normal add writes blocks to blockstore, syncs block and filestore datastore prefixes through `syncDagService`, and may pin. `OnlyHash` uses null datastore/mock DAG and does not persist or pin. `NoCopy` may write filestore references depending on configuration. Get/list are read-only but may fetch blocks.

Dependencies and integration points: core path for CLI `add/get/ls` via CoreAPI. Integrates repo config, blockstore/baseBlocks, exchange, pinning, filestore, MFS, coreunix adder, UnixFS HAMT/file metadata, CID builders, and tracing.

Risks: add option surface is broad; incorrect combinations can affect persistence, pinning, or CID determinism. Only-hash uses mock MFS root to avoid writes. Listing can block or return nil on context cancellation in `lsFromDirLinks`, and `lsFromLinks` sends to output without a context select while draining buffered links.

Test signals: heavily exercised by shared CoreAPI tests and `path_test.go` HAMT partial-resolution regression.
