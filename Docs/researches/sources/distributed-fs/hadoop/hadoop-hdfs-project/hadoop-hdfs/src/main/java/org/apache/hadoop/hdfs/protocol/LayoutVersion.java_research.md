# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/LayoutVersion.java

Purpose: Tracks HDFS layout-version feature history and provides helpers for building feature maps, checking whether a layout version supports a feature, and deriving current/minimum-compatible layout versions.

Important APIs and types: `BUGFIX_HDFS_2991_VERSION` marks a historical edit-log workaround. `LayoutFeature` is the interface implemented by layout feature enums. `Feature` enumerates pre-rolling-upgrade layout changes from quotas through protobuf fsimage and extended ACL support, including reserved release versions. `FeatureInfo` stores layout version, ancestor version, minimum compatible version, description, reserved status, and special features. `updateMap()`, `supports()`, `getCurrentLayoutVersion()`, `getMinimumCompatibleLayoutVersion()`, and `getString()` are the main helpers.

Control flow: `updateMap()` starts with existing features, checks that features are listed in non-increasing minimum-compatible layout-version order, copies the ancestor feature set for each new layout version, adds any special features, then adds the feature itself. `supports()` looks up a version's sorted feature set. Current and minimum-compatible versions are derived from the last non-reserved feature in the supplied enum array.

State and persistence behavior: This class does not persist state directly, but its constants define compatibility contracts for NameNode/DataNode storage directories, fsimage, and edit logs. Maps passed to `updateMap()` are mutated with layout-version-to-feature-set entries.

Dependencies and integration points: Depends on Java collections and is extended/used by NameNode and DataNode layout version classes. Feature entries correspond to on-disk layout changes in HDFS storage and edit/fsimage formats.

Risks: Feature ordering, ancestor links, and reserved markers are upgrade-critical. A wrong layout version can make newer software misread old storage or allow unsafe downgrade/rolling-upgrade behavior. `updateMap()` throws assertion errors for ordering issues, which are build/test signals rather than recoverable runtime errors.

Test signals: Tests should validate complete feature maps, support checks for representative versions, current/minimum-compatible version derivation excluding reserved entries, ancestor/special feature inheritance, ordering assertion failures, and historical compatibility such as `BUGFIX_HDFS_2991_VERSION` behavior.
