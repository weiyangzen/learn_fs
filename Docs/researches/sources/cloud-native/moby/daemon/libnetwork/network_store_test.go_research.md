# sources/cloud-native/moby/daemon/libnetwork/network_store_test.go

## Purpose
Unit test for controller network store/cache helpers.

## Important APIs, Types, And Functions
`TestNetworkStore` constructs a controller, stores two synthetic networks, exercises `findNetworks` with no filter and `filterNetworkByConfigFrom`, deletes one network, and stores the remaining network again.

## Control Flow
The test sorts found networks by ID before comparing expected pointer identities and lengths.

## State And Persistence
Uses a temporary data dir and real controller store/cache. Synthetic `Network` objects have minimal fields (`id`, `configFrom`).

## Dependencies And Integration Points
Depends on controller construction via `New`, `config.OptionDataDir`, and `gotest.tools` assertions.

## Risks
The test focuses on cache/store helper behavior, not datastore conflict or serialization edge cases.

## Test Signals
Confirms `findNetworks` returns cached pointers, config-from filtering works, deletion removes from cache, and re-storing an existing object succeeds.
