# sources/distributed-fs/eos/mgm/fsview/FsView.hh

## Purpose
`FsView.hh` declares the MGM filesystem-view model used by EOS to represent cluster topology by space, group, node, filesystem id, and geotag. It exposes the contracts used by registration/configuration code, balancers, schedulers, drainers, inspectors, command output, and tests. The header is not a thin declaration file: it defines several inline helpers and constructors, names the public view maps, and documents locking expectations for statistics and quota-sensitive operations.

## Important APIs, Types, And Functions
`FsBalanceInfo` and `FsPrioritySets` model filesystem candidates for balancing. Priority sets divide filesystems around group average fill into low, normal-low, normal-high, and high-priority buckets. `GeoTreeElement`, `GeoTreeNodeOrderHelper`, `GeoTreeAggregator`, and `GeoTree` define a reusable geotag tree with insertion, deletion, lookup, aggregation, size, and leaf iteration APIs.

`BaseView` extends `GeoTree` with a shared-hash locator, heartbeat timestamp, status, config accessors, table printing, and statistics APIs. `FsSpace`, `FsGroup`, and `FsNode` specialize it for space, group, and node views. `FsSpace` owns per-space balancing/draining/inspection components and default-parameter logic. `FsGroup` stores a group index. `FsNode` tracks shared-hash subscriptions, node active status, heartbeat freshness, refresh signaling, and a static instance counter for leak detection.

`FsView` exposes the central singleton and its public view maps: `mSpaceGroupView`, `mSpaceView`, `mGroupView`, `mNodeView`, and `mIdView`. It declares lifecycle operations (`Register`, `UnRegister`, `Reset`), movement (`MoveGroup`, `MoveNode` declaration), config persistence/application, mapping functions, print/df methods, quota checks, endpoint collection, balancer helpers, and heartbeat management. `DoubleAggregator` and `LongLongAggregator` are concrete `GeoTreeAggregator` implementations for floating-point and integer statistics.

## Control Flow
The declared flow is centered on `ViewMutex`: callers update the global maps through `FsView` registration APIs and query them through print/statistics helpers. `BaseView` statistics can optionally take the view lock, which allows aggregate calls to be reused inside already locked geotag aggregation. `FsView::HeartBeatCheck` is launched by the constructor through `AssistedThread` and joined in the destructor. Space construction starts companion worker objects, while `FsSpace::Stop` is available so `FsView::Reset` can stop threads before deleting views.

Geotag aggregation flow is declared in three stages: `GeoTree::runAggregator` initializes an aggregator with geotag labels and depth boundaries, then calls leaf and node aggregation bottom-up. The aggregators call back into `BaseView` to compute sums, averages, deviations, standard deviation, and counts for filesystem subsets.

## State And Persistence
`FsView` state is mostly in-memory pointers and registries. `mConfigEngine` is a non-owning pointer used for durable config writes, while `mFilesystemMapper` preserves fsid-to-uuid associations. `mUsageOk` caches quota decisions. `BaseView` persists config members through shared hashes and the config engine in implementation. `FsNode` owns a `SharedHashSubscription`, and `FsSpace` owns or references long-running worker objects. The header shows ownership is mixed: some members use `std::unique_ptr`, while `mGroupBalancer`, `mGeoBalancer`, and view maps use raw pointers and require disciplined destruction.

## Dependencies And Integration Points
The header depends on EOS common threading, locks, instance names, locators, symmetric keys, namespace metadata interfaces, filesystem registries, UUID mapping, shared-hash subscriptions, and platform statfs headers. Forward declarations connect it to `Balancer`, `GroupBalancer`, `GroupDrainer`, `GeoBalancer`, `Converter`, `IConfigEngine`, `FsBalancer`, and `FileInspector`. External users can directly inspect several public maps, so the class is both an API and a shared data structure.

## Risks
The broad public surface makes invariants difficult to enforce. Public mutable maps allow integration code to bypass registration helpers unless it follows locking and ownership rules. Raw pointer ownership for views and some worker objects raises leak and double-delete risk during reset, failover, and partial registration failures. The constructor starts the heartbeat thread immediately, which can surprise tests unless global dependencies are initialized. Aggregators require `setView` before `runAggregator`; this is enforced by `assert`, not by type structure. The deprecated `std::iterator` base in `GeoTree::const_iterator` may create future build issues with newer C++ standards.

## Test Signals
Header-level behavior should be covered through compile tests and focused unit tests for type contracts: `FsPrioritySets` ordering, `GeoTree` iterator behavior, aggregator initialization requirements, `FsNode` instance counting, and `FsView` lifecycle with `start/stop/reset` under test harness globals. API-level tests should assert that public print format functions continue to include required keys for monitoring consumers.
