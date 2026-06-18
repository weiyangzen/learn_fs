# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSClusterWithNodeGroup.java

## Purpose
`MiniDFSClusterWithNodeGroup` extends `MiniDFSCluster` to support network-topology tests that include node groups below racks. It lets tests map DataNodes to rack plus node-group paths while still using MiniDFSCluster lifecycle behavior.

## Important APIs, Types, and Functions
- Static `setNodeGroups(String[])` stores node-group assignments used during parent-class initialization.
- The constructor accepts a normal `MiniDFSCluster.Builder` and delegates to `super(builder)`.
- The main `startDataNodes(...)` overload adds `String[] nodeGroups` between racks and hosts and otherwise mirrors much of `MiniDFSCluster.startDataNodes`.
- Simpler overloads pass `nodeGroups` through for tests.
- The overridden parent-signature `startDataNodes(...)` injects static `NODE_GROUPS` so builder-driven cluster initialization can use node groups.

## Control Flow
Startup validation checks storage capacity/simulated capacity exclusivity, storage type/capacity array lengths, `StartupOption.RECOVER`, host config behavior, rack length, node-group length, host length, and simulated capacity length. It generates hostnames when racks are provided without hosts, prepares rollback args when needed, then loops over the requested DataNodes.

For each DN it clones config, sets loopback addresses, creates managed storage dirs, enables simulated capacity if requested, sets hostnames, and records topology mappings. If node groups are absent, it maps host and transfer address to the rack. If node groups are present, it concatenates rack and node-group strings and maps both the hostname and IP:port service to that combined topology path. It then instantiates and runs the DataNode, records `DataNodeProperties`, increments the cluster count, waits active, and applies optional volume capacity overrides.

## State and Persistence Behavior
The class adds static mutable state through `NODE_GROUPS`, which is consumed by the override called from the base constructor. Per-instance runtime state is inherited: `dataNodes`, `numDataNodes`, storage dirs, base dirs, and topology mappings. Persistent storage layout is the same as `MiniDFSCluster`; the only semantic difference is the topology path registered in `StaticMapping`.

## Dependencies and Integration Points
It depends on inherited MiniDFSCluster internals, especially protected `dataNodes`, `numDataNodes`, `storagesPerDatanode`, `makeDataNodeDirs`, `setupDatanodeAddress`, and `waitActive`. It integrates with `StaticMapping`, `NetUtils`, `DataNode`, `SecureDataNodeStarter`, `SimulatedFSDataset`, and `FsVolumeImpl`. Tests using rack/node-group placement policies depend on this subclass to represent node-group locality.

## Risks and Edge Cases
- `NODE_GROUPS` is static, so concurrent or sequential tests can leak node-group assignments unless reset.
- Rack and node-group strings are concatenated directly; callers must include expected separators in values if topology paths require them.
- The storage-capacity application block increments `curDatanodesNum` before looping and then indexes `dns[i]`, which is suspicious because `dns` is zero-based for the newly started DNs. This path looks error-prone for non-null `storageCapacities`.
- This subclass does not include all newer base-class features, such as DN config overlays or explicit HTTP/IPC port arrays, in its node-group-specific overload.
- Secure startup catches secure-resource exceptions by printing stack traces and continuing, matching older test style but making failures less explicit.

## Test Signals
The main signal is whether placement-policy tests observe expected rack/node-group paths through HDFS block placement. Constructor-driven startup also verifies that the parent override correctly uses `NODE_GROUPS`. Capacity override tests would be especially valuable because that path appears fragile.
