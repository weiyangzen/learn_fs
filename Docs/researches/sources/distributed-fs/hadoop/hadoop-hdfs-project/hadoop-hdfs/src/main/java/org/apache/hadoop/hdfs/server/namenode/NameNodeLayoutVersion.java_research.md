# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NameNodeLayoutVersion.java

## Purpose
`NameNodeLayoutVersion` defines NameNode metadata layout features and the version-to-feature map used to decide storage compatibility, rolling-upgrade downgrade compatibility, and feature support for fsimage/edit processing.

## Important APIs and Types
- `FEATURES` maps layout version integers to sorted sets of `LayoutFeature`.
- `CURRENT_LAYOUT_VERSION` and `MINIMUM_COMPATIBLE_LAYOUT_VERSION` are derived from the declared feature enum.
- `getFeatures(int lv)` returns features for a layout version.
- `supports(LayoutFeature f, int lv)` checks feature support against the NameNode feature map.
- `Feature` enum lists NameNode-specific layout changes from rolling upgrade through NVDIMM support, each carrying `FeatureInfo`.

## Control Flow
Static initialization merges common `LayoutVersion.Feature` values and NameNode-specific `Feature` values into `FEATURES`. Each enum constant declares its layout version, ancestor layout where needed, minimum compatible version, and description. Compatibility checks are delegated to `LayoutVersion.supports`.

## State and Persistence Behavior
There is no mutable runtime state after class initialization. The values directly control persistent metadata compatibility: VERSION layout numbers and feature-gated fsimage/edit behavior must match this table.

## Dependencies and Integration Points
`NNStorage`, fsimage loaders/savers, edit-log code, upgrade/rollback logic, and rolling-upgrade flows call `NameNodeLayoutVersion.supports` or use `CURRENT_LAYOUT_VERSION`. It depends on `LayoutVersion`, `LayoutVersion.FeatureInfo`, and `LayoutVersion.LayoutFeature`.

## Risks and Edge Cases
- Adding a feature with the wrong ancestor or minimum compatible version can break rolling downgrade guarantees.
- `getFeatures` may return null for unknown layout versions; callers need to handle invalid versions through higher-level storage checks.
- Feature descriptions are documentation, but the numeric version and compatibility values are operationally critical.

## Test Signals
Coverage is usually indirect through fsimage/edit-log compatibility, upgrade, rollback, and rolling-upgrade tests. `TestNameNodeRecovery`, `TestStartup`, and upgrade tests exercise current layout values when creating or reading metadata.
