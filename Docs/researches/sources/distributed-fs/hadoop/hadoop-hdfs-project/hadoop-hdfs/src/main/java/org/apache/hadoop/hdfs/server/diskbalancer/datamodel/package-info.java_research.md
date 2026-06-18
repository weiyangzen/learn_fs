# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/package-info.java

Purpose: package documentation for the diskbalancer data model.

Important APIs/types/functions: declares the package and describes the hierarchy: `DiskBalancerCluster` contains `DiskBalancerDataNode`; nodes contain `DiskBalancerVolumeSet`; volume sets contain `DiskBalancerVolume`.

Control flow: none.

State and persistence behavior: documents that model information is read from NameNode or user-supplied JSON.

Dependencies and integration points: provides high-level context for connector output and planner input.

Risks: documentation-only; it should stay aligned with model hierarchy if classes evolve.

Test signals: not directly tested.
