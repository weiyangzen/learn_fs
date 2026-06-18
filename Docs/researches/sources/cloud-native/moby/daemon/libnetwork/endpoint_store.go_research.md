# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_store.go

Purpose: centralizes endpoint persistence and the controller's in-memory endpoint cache. Important APIs are `Controller.storeEndpoint`, `deleteStoredEndpoint`, `cacheEndpoint`, `findEndpoints`, and `filterEndpointByNetworkId`.

Control flow: `storeEndpoint` writes the endpoint to the datastore through `updateToStore`, then caches the same pointer. `deleteStoredEndpoint` deletes from store, then removes the cache entry under `endpointsMu`. `findEndpoints` locks the cache and returns values filtered through `maputil.FilterValues`; the comment warns callers that returned endpoint pointers are not copies. `filterEndpointByNetworkId` matches endpoints whose network pointer has the expected ID.

State/dependencies: persistent state is in the controller datastore, while runtime state is `Controller.endpoints` guarded by `endpointsMu`. Dependencies include `context` and internal `maputil`. Risks include cache/store divergence if store updates fail, callers mutating returned pointers without endpoint locks, and filter functions dereferencing partially hydrated endpoints. Tests validate insert/find/delete/cache behavior with a temp controller datastore.
