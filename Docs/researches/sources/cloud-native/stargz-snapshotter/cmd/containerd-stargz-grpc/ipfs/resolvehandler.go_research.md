# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/ipfs/resolvehandler.go

Purpose: Implements an `fs/remote` resolve handler that turns IPFS descriptors into fetchers for lazy layer reads.

Important APIs/types: `ResolveHandler.Handle`, `fetcher.Fetch`, `fetcher.Check`, and `fetcher.GenID`. `Handle` extracts a CID from the OCI descriptor, discovers the local IPFS HTTP API address, stats the CID for size, and returns a range-capable fetcher.

Control flow: `Fetch` validates offset against known blob size, converts offset and size to `int`, and calls the IPFS client `Get("/ipfs/"+cid, &off, &size)`. `Check` repeats `StatCID`. `GenID` produces a SHA-256 key from CID, offset, and size.

State and persistence: Holds CID, size, and IPFS client in memory. No local persistence.

Dependencies and integration: Registered by `fsopts.ConfigFsOpts` when IPFS is enabled. Depends on IPFS descriptor helpers, IPFS client configuration, environment variable `IPFS_PATH`, and `remote.Fetcher`.

Risks: Only HTTP is supported. Offset/size conversion from int64 to int can overflow on 32-bit platforms or huge ranges. Fetch accepts `off == size`, which likely returns EOF/empty from IPFS. CID stat failures prevent lazy resolution.

Test signals: No direct tests in this subset; requires IPFS daemon or mocked client for coverage.
