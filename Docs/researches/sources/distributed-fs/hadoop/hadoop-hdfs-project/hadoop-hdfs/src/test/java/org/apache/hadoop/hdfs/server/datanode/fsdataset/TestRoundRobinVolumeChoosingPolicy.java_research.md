# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/TestRoundRobinVolumeChoosingPolicy.java

Purpose: This unit test validates `RoundRobinVolumeChoosingPolicy` volume selection by order, requested block size, additional reserved free space, out-of-space messages, and independent cursors for heterogeneous storage types.

Important APIs/types/functions: `RoundRobinVolumeChoosingPolicy`, `VolumeChoosingPolicy.chooseVolume`, `FsVolumeSpi.getAvailable`, `FsVolumeSpi.getStorageType`, `StorageType.DISK/SSD`, `DFS_DATANODE_ROUND_ROBIN_VOLUME_CHOOSING_POLICY_ADDITIONAL_AVAILABLE_SPACE_KEY`, and `DiskOutOfSpaceException`.

Control flow: Helper methods build mocked volume lists and assert chosen volume sequences. Basic RR alternates two volumes, skips too-small volumes for larger blocks, and throws when none fit. Additional-space tests require configured headroom. Exception-message tests verify exact message including largest available bytes and block size. Storage-type tests call the same policy with separate disk and SSD lists and assert independent round-robin behavior.

State and persistence behavior: State is policy cursor state and mocked available space; no real volumes are touched.

Dependencies and integration points: It covers the default DataNode volume chooser and provides reusable helper methods for `AvailableSpaceVolumeChoosingPolicy`.

Risks and test signals: Signals are exact selected mock objects and exception messages. Risk is brittleness if messages or cursor semantics change intentionally.
