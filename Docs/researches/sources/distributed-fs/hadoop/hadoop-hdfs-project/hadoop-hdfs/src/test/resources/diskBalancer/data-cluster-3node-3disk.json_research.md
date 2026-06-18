# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/diskBalancer/data-cluster-3node-3disk.json

## Purpose
This JSON fixture describes a three-node DiskBalancer cluster with three storage types and three volumes per storage type per node. It is used to test DiskBalancer data-model parsing, density calculations, and planner behavior over a non-trivial but deterministic cluster shape.

## Important APIs, types, and functions
The top-level object contains `nodes`, empty `exclusionList`, empty `inclusionList`, and `threshold: 0`. Each node has a `dataNodeUUID`, `nodeDataDensity`, and `volumeSets` keyed by `SSD`, `RAM_DISK`, and `DISK`. Each volume entry includes path, capacity, used bytes, reserved bytes, storage type, UUID, failed flag, volume data density, and transient flag.

## Control flow
There is no executable control flow. DiskBalancer tests read the fixture into cluster/node/volume-set/volume model objects and then run validation or planning logic.

## State and persistence behavior
The file is static model state. It encodes mixed capacities, used/reserved values, transient and non-transient storage, and density values that downstream tests treat as expected input data.

## Dependencies and integration points
It integrates with DiskBalancer JSON serde, `DiskBalancerCluster`, node and volume-set models, planner steps, inclusion/exclusion filters, and threshold-based balancing decisions.

## Risks and edge cases
The fixture uses escaped `/tmp/disk/...` paths and large numeric capacities/usage values that must be parsed as long-compatible numbers. All `failed` flags are false and inclusion/exclusion lists are empty, so it does not cover failed-volume or filtered-node behavior. `threshold: 0` can make planners sensitive to any imbalance.

## Test signals
Successful use of this fixture indicates DiskBalancer can parse multi-node, multi-storage-type clusters, preserve transient flags for RAM_DISK, retain UUID/path/capacity/usage metadata, and compute or consume node/volume density information.
