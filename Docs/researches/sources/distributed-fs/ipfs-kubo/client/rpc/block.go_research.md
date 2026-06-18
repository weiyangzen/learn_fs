# sources/distributed-fs/ipfs-kubo/client/rpc/block.go

## Purpose
This file implements `coreiface.BlockAPI` over Kubo's HTTP RPC endpoints.

## Important APIs, Types, And Functions
`BlockAPI` wraps `HttpApi`. `blockStat` implements size and immutable path. `Put` maps CID prefix options to `block/put` flags, `Get` fetches block bytes, `Rm` removes a block with optional force, and `Stat` returns block metadata.

## Control Flow
`Put` validates multihash type, chooses `format=v0` for CIDv0 dag-pb or `cid-codec` otherwise, uploads a multipart body, decodes `Key` and `Size`, and parses the CID. `Get`, `Rm`, and `Stat` normalize not-found text into IPLD-compatible errors where possible.

## State And Persistence Behavior
`Put` and `Rm` mutate the remote blockstore/pin behavior according to options. `Get` and `Stat` are read-only.

## Dependencies And Integration Points
It integrates coreiface block options, multicodec/multihash mappings, HTTP request builders, and error parsing helpers.

## Risks And Test Signals
Risks include typoed error text, codec string compatibility, buffering full block data in memory, and not-found parsing brittleness. Signals are block add/get/stat/remove behavior in CoreAPI tests.
