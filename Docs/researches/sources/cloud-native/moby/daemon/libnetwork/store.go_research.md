## sources/cloud-native/moby/daemon/libnetwork/store.go

Purpose: Implements libnetwork controller helpers for loading, updating, deleting, caching, and cleaning persisted network and endpoint objects from the configured datastore. This is the persistence bridge between in-memory `Controller`, `Network`, and `Endpoint` state and the `datastore.KVObject` backend.

Important APIs and functions: `Controller.getNetworkFromStore`, `getNetworks`, and `getNetworksFromStore` enumerate persisted `Network` objects, restore their `ctrlr` pointer, default empty scope to `scope.Local`, and optionally cache them. `Network.getEndpointFromStore` and `getEndpointsFromStore` restore endpoints and cache them in the controller. `Controller.updateToStore` wraps `PutObjectAtomic` with an OpenTelemetry span and preserves `datastore.ErrKeyModified` for optimistic-lock callers. `deleteFromStore` retries `DeleteObjectAtomic` after refreshing the object on `ErrKeyModified`. `networkCleanup` scans persisted networks marked `inDelete` and invokes `n.delete(true, true)`.

Control flow and state: List operations tolerate missing keys as empty state, but propagate or log other store errors depending on caller strictness. Objects loaded from the store are mutable in-memory objects whose controller pointer is reattached; `getNetworksFromStore` locks each network while mutating `ctrlr` and `scope`. Deletion uses a goto retry loop to converge on the latest KV revision.

Dependencies and integration points: Relies on the libnetwork datastore abstraction, `scope.Local`, controller endpoint/network caches, containerd logging, and OpenTelemetry tracing. Network cleanup integrates with network delete semantics and is sensitive to the `inDelete` persisted flag.

Risks: Retrying delete without an explicit retry limit can spin if the store is continually modified. `context.TODO()` in several paths limits cancellation observability. `getNetworks` and `getNetworksFromStore` overlap but differ in caching and error behavior, which the FIXME notes as a maintenance risk.

Test signals: The adjacent store tests validate persistence, restore, and non-persistence behavior for networks and endpoints through controller restarts.
