## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BlockStoragePolicySpi.java

Purpose: stable public SPI describing a block storage placement policy independently of HDFS implementation classes.

Important APIs and types: exposes policy name, preferred `StorageType[]`, creation fallbacks, replication fallbacks, and `isCopyOnCreateFile()` for inherit-only policies.

Control flow: interface only; concrete policy classes supply arrays and flags.

State and persistence behavior: no state in the interface. Implementations represent policy metadata that may come from namenode policy definitions.

Dependencies and integration points: returned from `AbstractFileSystem.getStoragePolicy` and `getAllStoragePolicies`; used by filesystem clients that need storage-type placement information.

Risks: array return values can be mutable depending on implementation. Callers should not assume HDFS-only policy names or storage types.

Test signals: implementation tests should assert stable names, fallback arrays, copy-on-create semantics, and defensive-copy behavior if promised by the implementation.
