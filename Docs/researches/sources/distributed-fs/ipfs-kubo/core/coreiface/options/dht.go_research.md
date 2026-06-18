# sources/distributed-fs/ipfs-kubo/core/coreiface/options/dht.go

## Purpose
Maintains deprecated DHT option aliases for the routing option API.

## Important APIs, Types, and Functions
Aliases `DhtProvideSettings`, `DhtFindProvidersSettings`, option function types, `DhtProvideOptions`, `DhtFindProvidersOptions`, and `Dht` to their routing equivalents.

## Control Flow and State
There is no runtime flow. Alias declarations keep old import paths source-compatible without duplicating state.

## Dependencies and Integration Points
Depends on `options/routing.go` definitions in the same package. It supports older callers while the CoreAPI exposes `Routing`.

## Risks and Test Signals
Risks include alias drift if routing option types change and deprecated docs falling out of sync. Compile coverage of old DHT option users is the main signal.
