## sources/cloud-native/moby/daemon/internal/layer/layer_store_windows.go

Purpose: Exposes descriptor-aware registration on Windows builds.

Important API: `(*layerStore).RegisterWithDescriptor(ts, parent, descriptor)` delegates to `registerWithDescriptor`.

Control flow and state: No additional logic; build tags/platform filename select this implementation.

Dependencies and integration: Allows Windows layer store to satisfy `DescribableStore`, so tar load can preserve foreign source descriptors when registering layers.

Risks: Behavior is entirely inherited from `registerWithDescriptor`; platform-specific differences are in graphdriver behavior. No direct tests in this subset.

Persistence: Same as `layer_store.go` through metadata transactions.
