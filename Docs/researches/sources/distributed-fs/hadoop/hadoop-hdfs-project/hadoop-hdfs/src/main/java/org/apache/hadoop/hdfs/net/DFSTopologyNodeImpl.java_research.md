# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/net/DFSTopologyNodeImpl.java

Purpose: Implements the HDFS-specific inner topology node that augments `InnerNodeImpl` with per-subtree storage-type counts. These counts allow `DFSNetworkTopology` to select DataNodes by `StorageType` without scanning the whole topology.

Important APIs and types: `FACTORY` creates `DFSTopologyNodeImpl` inner nodes for topology initialization. `getSubtreeStorageCount(StorageType)` reads aggregate counts. Overridden `add(Node)` and `remove(Node)` maintain topology children and storage counts. `childAddStorage(String, StorageType)` and `childRemoveStorage(String, StorageType)` propagate storage-type count changes from descendants. `getChildrenStorageInfo()` exposes internal count maps for tests.

Control flow: `add()` validates descendant and DataNode type. If the current node is the direct parent, it inserts or replaces the DataNode, initializes child storage info, increments aggregate counts, or updates existing storage info on duplicate add. Otherwise it creates/fetches the next ancestor inner node, recurses, increments leaf count, updates the child-name count map, and increments aggregate counts. `remove()` mirrors this process, decrementing counts and removing empty inner child nodes. Storage update callbacks adjust child and aggregate counts then recurse to the parent.

State and persistence behavior: State is in-memory topology metadata: inherited `children`, `childrenMap`, `numOfLeaves`, and two maps, `childrenStorageInfo` and `storageTypeCounts`. Counts represent number of DataNodes in the subtree that expose each storage type, not number of physical volumes. There is no disk persistence, but this state is long-lived in the NameNode block manager topology.

Dependencies and integration points: Depends on `DatanodeDescriptor` for storage type membership, Hadoop topology `InnerNodeImpl`/`InnerNode`/`Node`, and `StorageType`. It is used by `DFSNetworkTopology` through the factory.

Risks: Count synchronization is delicate across duplicate adds, storage-type changes, removals, and empty inner-node cleanup. `updateExistingDatanode()` mutates a map while iterating over its key set, which is a concurrency/iteration risk in standard Java collections if removal occurs during iteration. Some methods assume callers synchronize or hold topology locks; direct calls without locking can race. Count semantics may be wrong if future placement needs per-storage-instance counts rather than per-DataNode type presence.

Test signals: Tests should add/remove DataNodes with one and multiple storage types, duplicate-add with changed types, child storage add/remove callbacks, multi-level subtree counts, empty inner-node removal, invalid node type rejection, non-descendant rejection, and integration with storage-aware random selection.
