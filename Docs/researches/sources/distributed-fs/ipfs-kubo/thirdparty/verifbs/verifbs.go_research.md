## sources/distributed-fs/ipfs-kubo/thirdparty/verifbs/verifbs.go

Purpose: wraps Boxo blockstores to enforce CID validation on reads and writes.

Important APIs/types/functions: `VerifBSGC` embeds `bstore.GCBlockstore`; `VerifBS` embeds `bstore.Blockstore`. Both override `Put`, `PutMany`, and `Get`, calling `verifcid.ValidateCid(verifcid.DefaultAllowlist, ...)` before delegating to the embedded store. `PutMany` validates every block before writing any batch.

State and persistence: wrappers do not store state themselves; they guard operations against the underlying persistent blockstore.

Dependencies and integration points: depends on `github.com/ipfs/boxo/blockstore`, `github.com/ipfs/boxo/verifcid`, go-block-format blocks, and go-cid. It integrates with repo/blockservice construction where blockstores should reject insecure CIDs.

Risks and test signals: wrappers only cover `Put`, `PutMany`, and `Get`; other methods inherited from the embedded interfaces may bypass validation if they accept CIDs. The CID security sharness test provides black-box signals for this layer.
