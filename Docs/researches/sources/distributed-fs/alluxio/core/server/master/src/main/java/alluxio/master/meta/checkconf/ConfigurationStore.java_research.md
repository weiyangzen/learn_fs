# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigurationStore.java

## Purpose
`ConfigurationStore` records reported configuration for a class of nodes and tracks which registered nodes are currently lost. It provides live-node configuration snapshots for consistency checking.

## Important APIs and Types
- `Map<Address, List<ConfigRecord>> mConfMap` stores node configs.
- `Set<Address> mLostNodes` filters out lost nodes.
- `List<Runnable> mChangeListeners` notifies checkers.
- `registerNewConf(Address, List<ConfigProperty>)` converts gRPC config properties to `ConfigRecord`s.
- `handleNodeLost`, `lostNodeFound`, and `handleNodeDelete` update liveness/deletion state.
- `getConfMap()` returns a copy containing only non-lost nodes.
- `getLiveNodeAddresses()` returns non-lost known addresses.
- `registerChangeListener(Runnable)` installs dirty callbacks.

## Control Flow
All mutating and read methods are synchronized. Registering new config validates inputs, converts property names with `toPropertyKey`, stores the records, removes the node from lost state, then runs listeners. Unknown property names are converted into unregistered `PropertyKey` instances so mixed-version or UFS-specific worker configs can still be represented.

## State and Persistence
State is in-memory; it reflects currently known node reports and lost-node flags. It is not journaled in this class.

## Dependencies and Integration Points
Used by `ConfigurationChecker` for master and worker stores. Integrates with gRPC `ConfigProperty`, wire `Address`, and `PropertyKey` registry.

## Risks and Edge Cases
- `getConfMap` creates a new map but reuses the `List<ConfigRecord>` instances, so consumers should not mutate lists or records.
- `reset` does not run change listeners, so callers expecting dirty reports after reset must handle that externally.
- Listener callbacks run while holding the store monitor; expensive callbacks could block store updates.

## Test Signals
Tests should cover unknown property conversion, live/lost/delete transitions, listener invocation, filtering of lost nodes, and reset behavior.
