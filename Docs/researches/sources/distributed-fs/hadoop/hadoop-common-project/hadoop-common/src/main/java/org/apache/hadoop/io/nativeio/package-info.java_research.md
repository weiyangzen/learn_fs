<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/package-info.java

## Purpose
`package-info.java` documents and annotates the `org.apache.hadoop.io.nativeio` package as Hadoop-private and unstable.

## Important APIs and Types
The file applies package-level `@InterfaceAudience.Private` and `@InterfaceStability.Unstable` annotations.

## Control Flow
There is no executable control flow.

## State and Persistence
There is no runtime or persistent state. Its effect is metadata for API classification and generated documentation.

## Dependencies and Integration Points
It imports Hadoop classification annotations and applies them to all native I/O package documentation.

## Risks and Edge Cases
The package-level classification signals that downstream users should not depend on API stability. If public usage grows, changes in this package can still break external consumers despite the annotation.

## Test Signals
No functional tests are needed; source or doc checks can verify package annotations remain present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/package-info.java -->
