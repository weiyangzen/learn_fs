<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLayoutVersion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLayoutVersion.java

Purpose: Validates layout-version feature inheritance, reserved release compatibility, NameNode/DataNode feature ordering, and minimum compatible layout-version policy.

Important APIs/types/functions: `LayoutVersion.Feature`, `FeatureInfo`, `LayoutFeature`, `NameNodeLayoutVersion`, `DataNodeLayoutVersion`, `LayoutVersion.updateMap`, `getMinimumCompatibleLayoutVersion`, and Mockito-created invalid `LayoutFeature`.

Control flow: Tests iterate common and NameNode feature enums to ensure every feature supports its ancestor set. Specific release tests assert reserved release versions support delegation tokens or concat. NameNode/DataNode first feature tests ensure feature-specific enums inherit all non-reserved common features. Minimum-compatible tests check the truncate-era compatibility group, require descending enum order by minimum compatible layout version, assert out-of-order updates fail fast, and pin the current minimum compatible layout version. `testSNAPSHOT` enforces that snapshot support implies fsimage name optimization support.

State and persistence behavior: No runtime persistence. The file guards serialized filesystem image/edit-log compatibility metadata embedded in enums.

Dependencies and integration points: Directly protects rolling upgrade, downgrade, fsimage, and edit-log layout compatibility contracts for NameNode and DataNode code.

Risks: Intentional compatibility-breaking changes must update pinned expectations. Enum ordering is semantic here, so refactors can fail tests even without behavior changes.

Test signals: Passing indicates layout feature ancestry and minimum-compatible version rules remain coherent and downgrade policy has not changed accidentally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLayoutVersion.java -->
