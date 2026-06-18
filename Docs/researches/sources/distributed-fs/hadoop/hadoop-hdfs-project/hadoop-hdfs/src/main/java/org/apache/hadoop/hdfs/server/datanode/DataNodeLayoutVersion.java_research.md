## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataNodeLayoutVersion.java

Purpose: defines the DataNode-specific layout version feature matrix and current DataNode layout version. It layers DataNode storage features on top of the shared HDFS `LayoutVersion` features.

Important APIs and types: `FEATURES` maps layout versions to sorted feature sets. `getCurrentLayoutVersion()` returns the current DataNode layout version derived from the enum. `setCurrentLayoutVersionForTesting(int)` overrides it for rolling-upgrade tests. `getFeatures(int)` and `supports(LayoutFeature, int)` query the matrix. The nested `Feature` enum implements `LayoutFeature` and currently defines `FIRST_LAYOUT`, `BLOCKID_BASED_LAYOUT`, and `BLOCKID_BASED_LAYOUT_32_by_32`.

Control flow: static initialization first loads common `LayoutVersion.Feature` values into `FEATURES`, then overlays DataNode-specific features. The current layout version is computed from `Feature.values()`. Storage code calls `supports` to decide how to parse VERSION files, whether federation or UUID features are present, whether legacy RBW/detach layouts apply, and whether block-ID directory upgrades are required.

State and persistence: the class itself only holds in-memory static metadata. Its values directly control persistent storage transitions in `DataStorage`, including VERSION file layout, upgrade checks, rollback compatibility, and hard-link migration from old layouts to the 32-by-32 block-ID-based directory tree.

Dependencies and integration points: depends on `org.apache.hadoop.hdfs.protocol.LayoutVersion`, `FeatureInfo`, and `LayoutFeature`. `DataStorage` calls `getCurrentLayoutVersion` during format/upgrade, `supports` during property read/write and layout transitions, and references `Feature.BLOCKID_BASED_LAYOUT_32_by_32` when upgrading finalized block directories.

Risks: layout version mistakes are persistent and hard to recover from. Adding a new feature with an incorrect ancestor, reserved flag, or version number can make upgrades/rollbacks reject valid disks or accept incompatible disks. The testing override is package-private but static; tests must restore it after use.

Test signals: storage upgrade, rollback, rolling-upgrade, and layout-version matrix tests should verify `supports` across old and current versions, validate current layout version expectations, and exercise DataStorage transitions for pre-federation, federation, UUID, and block-ID-layout cases.
