# sources/distributed-fs/ipfs-kubo/client/rpc/name.go

## Purpose
This file implements IPNS publish and resolve operations over HTTP RPC.

## Important APIs, Types, And Functions
`NameAPI` has `Publish`, `Search`, and `Resolve`. `ipnsEntry` models publish output. It uses coreiface name options and Boxo namesys resolve option processing.

## Control Flow
`Publish` sends `name/publish` with key, offline allowance, lifetime, TTL, and `resolve=false`, then converts the returned name string. `Search` and `Resolve` reject unsupported depths, map cache/recursive/DHT options to RPC flags, and decode streamed or single resolve outputs into paths.

## State And Persistence Behavior
Publish mutates IPNS records and may publish them depending on options. Resolve/search are read-only but may use or bypass resolver cache.

## Dependencies And Integration Points
It integrates IPNS, namesys depth semantics, Kubo `name/*` commands, and streaming JSON responses.

## Risks And Test Signals
Risks include unsupported custom depths, silent stream termination on path parse errors, and resolver option mismatch. Signals are CoreAPI name publish/resolve/search tests.
