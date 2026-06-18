# sources/distributed-fs/ipfs-kubo/assets/assets.go

## Purpose
This package embeds the default init documentation and seeds it into a newly initialized Kubo node.

## Important APIs, Types, And Functions
`Asset embed.FS` embeds `init-doc`. `SeedInitDocs` calls `addAssetList` over fixed paths such as `about`, `readme`, `help`, and `quick-start`. `addAssetList` creates a CoreAPI, loads embedded files, builds a `files.NewMapDirectory`, adds it through `Unixfs().Add`, pins the resulting path, and returns the root CID.

## Control Flow
Initialization code calls `SeedInitDocs`; every embedded path is read into a bytes file, added as a directory, then pinned.

## State And Persistence Behavior
It persists embedded docs into the node blockstore and pinset. Failure before pinning can leave partially added blocks depending on lower-level add behavior.

## Dependencies And Integration Points
It integrates Go `embed`, Kubo `coreapi`, Boxo `files`, UnixFS add, and pin APIs. `cmd/ipfs/kubo/init.go` uses this for non-empty repo initialization.

## Risks And Test Signals
Risks include missing embedded asset paths, add/pin failures, and initialization relying on a live in-process node. Signals are `ipfs init` printing a readable `/ipfs/<cid>/readme` path and the returned CID being pinned.
