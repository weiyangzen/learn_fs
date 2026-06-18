# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerDataNode.java

Purpose: data model for one DataNode, including identity, network address, volume sets grouped by storage type, volume count, and node data density used for report ranking.

Important APIs/types/functions: constructors initialize UUID and `volumeSets`. Standard getters/setters expose DataNode IP/name/port/UUID. `addVolume()` groups a `DiskBalancerVolume` into a `DiskBalancerVolumeSet` by storage type, creating the set with matching transient flag as needed, then recomputes node density. `computeNodeDensity()` sums absolute volume data densities across all volumes and updates volume count. `isBalancingNeeded()` delegates to all volume sets. `compareTo()` orders by node data density.

Control flow: connectors call setters and `addVolume()` for each storage report. Planner/report code reads volume sets and density. Sorting report output uses `Comparable` and reverse order to select high-density nodes.

State and persistence behavior: plain Java bean state serialized as part of cluster JSON. Density is derived but stored; every added volume recomputes set density and node density.

Dependencies and integration points: uses `DiskBalancerVolumeSet`, `DiskBalancerVolume`, and Hadoop `Preconditions`. Consumed by cluster lookup, report formatting, and greedy planning.

Risks: empty constructor does not initialize `volumeSets`, relying on Jackson to populate it; direct use must call setters or use UUID constructor. `equals()` compares UUID, but `hashCode()` delegates to `Object`, violating the equals/hashCode contract for hash collections. `compareTo()` subtracts doubles before comparing to zero, which is less direct than `Double.compare(this.nodeDataDensity, that.nodeDataDensity)`.

Test signals: data model tests and command tests validate node density sorting, volume grouping, and balancing need checks.
