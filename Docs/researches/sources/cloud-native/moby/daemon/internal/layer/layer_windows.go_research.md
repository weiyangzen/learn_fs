## sources/cloud-native/moby/daemon/internal/layer/layer_windows.go

Purpose: Adds Windows-specific layer path lookup and mount ID behavior.

Important APIs: `Getter` is a graphdriver extension for direct layer paths. `GetLayerPath(s Store, layer ChainID)` returns the host path for a layer. `(*layerStore).mountID(name)` returns the mount name itself.

Control flow: `GetLayerPath` asserts the store is a `*layerStore`, locks layer map, finds the read-only layer, then either calls driver `Getter.GetLayerPath(cacheID)` or mounts the driver layer with `Get` and immediately `Put`s it after capturing the path. `mountID` preserves the container/mount name due to Windows constraints.

State and persistence: Reads in-memory layer map and graphdriver state. No new persistence.

Dependencies and integration: Used by Windows daemon paths needing host layer paths. Integrates with graphdriver-specific Windows APIs.

Risks: The returned path from fallback `Get` may become invalid after `Put` depending on driver semantics. Holding `layerL` while calling driver methods may block other layer operations. Unsupported store types fail.

Tests: No direct tests in this subset.
