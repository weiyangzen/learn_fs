<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/streaming/manager.go -->
# sources/cloud-native/containerd/plugins/streaming/manager.go

## Purpose
Registers and implements containerd's in-memory streaming manager, including metadata GC integration for active and leased stream resources.

## Important APIs, Types, And Functions
Plugin ID is `manager` under `plugins.StreamingPlugin`. Main types are `streamManager`, `managedStream`, and `collectionContext`. APIs include `Register`, `Get`, `StartCollection`, `ReferenceLabel`, `managedStream.Close`, and collection methods `All`, `Active`, `Leased`, `Remove`, `Cancel`, and `Finish`.

## Control Flow
Initialization requires the metadata plugin, creates namespace/name and namespace/lease indexes, and registers the manager as a collectible metadata resource. `Register` records a stream under the current namespace and optional lease. `Get` looks up by namespace/name. GC collection locks the manager until canceled or finished; `Finish` removes marked streams from both indexes, unlocks, and then closes removed streams.

## State And Persistence
State is in-memory maps protected by an RW mutex. Stream liveness is not persisted across daemon restarts. Lease associations are tracked in `byLease` so metadata GC can keep leased streams.

## Dependencies And Integration Points
Integrates with metadata DB resource collection, leases context, namespaces, streaming core interface, GC nodes, errdefs, and plugin registry.

## Risks And Edge Cases
Collection holds the write lock for its full duration, blocking register/get/close. `managedStream.Close` removes indexes before closing the underlying stream; underlying close errors do not roll back map removal. Non-leased stream expiry is left as a TODO.

## Test Signals
No file-local tests in this subset. Expected coverage is via metadata GC and streaming service integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/streaming/manager.go -->
