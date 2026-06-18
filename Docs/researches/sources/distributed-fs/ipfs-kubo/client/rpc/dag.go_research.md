# sources/distributed-fs/ipfs-kubo/client/rpc/dag.go

## Purpose
This file implements an IPLD DAG service over the block HTTP API.

## Important APIs, Types, And Functions
Types include `HttpDagServ`, `httpNodeAdder`, and `pinningHttpNodeAdder`. Methods include `Get`, `GetMany`, `Add`, `AddMany`, `Pinning`, `Remove`, and `RemoveMany`.

## Control Flow
`Get` retrieves raw block bytes through `Block().Get`, wraps them in a block with the requested CID, and decodes with the API's IPLD decoder. `add` uploads `format.Node.RawData()` through `Block().Put`, preserving CID codec/hash details and verifying the remote CID matches. Multi operations loop sequentially except `GetMany`, which starts one goroutine per CID.

## State And Persistence Behavior
Adds and removes mutate the remote blockstore and optionally pin added nodes. Gets are read-only.

## Dependencies And Integration Points
It integrates go-ipld-format, go-block-format, CID prefixes, block API, and the registered decoder from `api.go`.

## Risks And Test Signals
Risks include unbounded `GetMany` goroutines, sequential add/remove inefficiency, and codec mismatch causing CID verification failure. Signals are CoreAPI DAG add/get/remove tests and CID equality checks.
