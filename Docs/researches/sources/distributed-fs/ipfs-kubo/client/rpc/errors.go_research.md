# sources/distributed-fs/ipfs-kubo/client/rpc/errors.go

## Purpose
This file converts textual HTTP API error messages back into ABI-compatible Go errors, especially IPLD not-found errors.

## Important APIs, Types, And Functions
`prePostWrappedNotFoundError` wraps an `ipld.ErrNotFound` while preserving surrounding text. `parseErrNotFoundWithFallbackToMSG`, `parseErrNotFoundWithFallbackToError`, `parseIPLDErrNotFound`, and `parseBlockstoreNotFound` implement parsing. `blockstoreNotFoundMatchingIPLDErrNotFound` makes old blockstore text match `ipld.IsNotFound`.

## Control Flow
Parsing first handles empty strings, then searches for `ipld: could not find`, extracts a CID or `node`, validates CID encoding, preserves pre/post text, and falls back to blockstore text matching.

## State And Persistence Behavior
No state or persistence; pure error conversion.

## Dependencies And Integration Points
It integrates CID parsing, multibase expectations, go-ipld-format error matching, and block/RPC methods that need typed not-found errors.

## Risks And Test Signals
Risks include fragile string parsing, future error wording changes, and rejecting valid but differently encoded CIDs. Dedicated tests cover wrapping, break characters, CID versions, undefined CIDs, and blockstore compatibility.
