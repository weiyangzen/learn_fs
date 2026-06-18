# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReservedSpaceCalculator.java

## Purpose

`ReservedSpaceCalculator` encapsulates DataNode policy for reserving local filesystem capacity for non-HDFS use. It supports absolute byte reservation, percentage reservation, and conservative/aggressive combinations of both.

## Important APIs, Control Flow, and State

`Builder` collects `Configuration`, `DF`, `StorageType`, and directory string, then reflectively constructs the configured calculator class from `DFS_DATANODE_DU_RESERVED_CALCULATOR_KEY`. The base class stores those inputs and resolves reservation configuration with specificity order: `key.dir.storageType`, `key.dir`, `key.storageType`, then base key/default. `getReserved()` is implemented by nested classes.

`ReservedSpaceCalculatorAbsolute` returns configured bytes. `ReservedSpaceCalculatorPercentage` returns `(DF.capacity * pct) / 100`. `ReservedSpaceCalculatorConservative` returns the larger of absolute and percentage values. `ReservedSpaceCalculatorAggressive` returns the smaller. The calculator has no persistence; it reads configuration and live filesystem capacity through `DF`.

## Dependencies, Integration, Risks, and Tests

Dependencies include `Configuration`, `DF`, `StorageType`, `StringUtils`, and DFS reserved-space config keys. It is used by `FsVolumeImpl` capacity/available accounting.

Risks include reflection failures wrapped as `IllegalStateException`, raw constructor usage, integer overflow in `total * percentage`, and surprising configuration precedence for per-directory/per-storage keys. Tests should cover each policy, precedence ordering, custom calculator construction, storage-type lowercase keys, and large-capacity percentage arithmetic.
