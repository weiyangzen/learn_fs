# sources/cloud-native/moby/daemon/libnetwork/network_store.go

## Purpose
Thread-safe controller helpers for persisting networks and maintaining the controller's in-memory network cache.

## Important APIs, Types, And Functions
`storeNetwork` writes a `Network` via `updateToStore` then caches it. `deleteStoredNetwork` deletes from the datastore and removes the cache entry. `cacheNetwork` inserts by network ID. `findNetworks` filters cached network pointers. `filterNetworkByConfigFrom` matches networks that depend on a named config-only network.

## Control Flow
Store/update succeeds before cache update. Delete succeeds in the datastore before cache removal. Cache access is protected by `networksMu`; `findNetworks` delegates value filtering to `maputil.FilterValues`.

## State And Persistence
Persistent state lives in the controller datastore through `updateToStore`/`deleteFromStore`; live state lives in `Controller.networks`. Returned `findNetworks` values are pointers to cached networks, not copies.

## Dependencies And Integration Points
Used by network creation, deletion, cleanup, and config-network reference checks in `network.go`. Depends on `maputil`.

## Risks
Callers must treat returned pointers carefully because the helper explicitly does not clone networks. Store/cache ordering means cache updates happen only after successful store operations.

## Test Signals
`network_store_test.go` verifies storing, filtering, deleting, pointer identity, and idempotent store update behavior.
