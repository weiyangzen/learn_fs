# sources/distributed-fs/ipfs-kubo/client/rpc/routing.go

## Purpose
This file implements routing record and provider operations over HTTP RPC.

## Important APIs, Types, And Functions
`RoutingAPI` exposes `Get`, `Put`, `FindPeer`, `FindProviders`, and `Provide`.

## Control Flow
`Get` decodes the first routing query event's base64 `Extra`. `Put` uploads value bytes to `routing/put` with optional offline allowance. `FindPeer` reads query events until `FinalPeer`. `FindProviders` resolves the path to a root CID, streams provider query events, and emits provider addr infos. `Provide` resolves a path and calls `routing/provide`.

## State And Persistence Behavior
Put and provide mutate routing/DHT state. Get/find operations read network routing state and may block on network activity.

## Dependencies And Integration Points
It integrates Kubo routing commands, libp2p routing query events, peer addr infos, path resolution, and coreiface routing options.

## Risks And Test Signals
Risks include limited error propagation from provider streams, assuming `FinalPeer` has a response, and base64 `Extra` coupling. Signals are CoreAPI routing tests for record get/put, peer lookup, provider lookup, and provide.
