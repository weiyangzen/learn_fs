# sources/distributed-fs/ipfs-kubo/core/coreiface/options/block.go

## Purpose
Builds option structs for block put and remove operations, including CID codec/hash settings and pin/force flags.

## Important APIs, Types, and Functions
Defines `BlockPutSettings`, `BlockRmSettings`, option function types, `BlockPutOptions`, `BlockRmOptions`, `Block` option namespace, and option methods `CidCodec`, `Format`, `Hash`, `Pin`, and `Force`.

## Control Flow and State
Defaults are CIDv1 raw with sha2-256 and no pinning. Options apply in order. `Format` preserves legacy names by mapping `v0`/`protobuf` to dag-pb and `cbor` to dag-cbor, and validates CIDv0 compatibility with dag-pb plus sha2-256-32.

## Dependencies and Integration Points
Depends on go-cid, go-multicodec, and go-multihash. Consumed by BlockAPI implementations and tested by block conformance cases.

## Risks and Test Signals
Risks include typo in error text (`sha2-255-32`), legacy format compatibility, option order interactions, and invalid CIDv0 combinations. Tests cover raw defaults, dag-cbor/dag-pb aliases, CIDv0, custom hash, pin, and force remove.
