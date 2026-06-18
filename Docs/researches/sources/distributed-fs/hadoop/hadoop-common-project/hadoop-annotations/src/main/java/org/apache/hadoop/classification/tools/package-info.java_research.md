# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/package-info.java

Purpose: package-level audience annotation for Hadoop classification doclet tools.

Important APIs, types, and functions: annotates `org.apache.hadoop.classification.tools` with `@InterfaceAudience.LimitedPrivate` for Hadoop-related projects including Common, Avro, Chukwa, HBase, HDFS, Hive, MapReduce, Pig, and ZooKeeper.

Control flow: no runtime control flow. The package annotation supplies metadata to documentation and API policy tooling.

State and persistence: package annotation metadata persists in compiled package metadata according to annotation retention.

Dependencies and integration points: imports `InterfaceAudience`; integrates the tools package with Hadoop's API audience classification.

Risks and test signals: package-level classification may not be considered by element-level filtering code that only inspects direct annotation mirrors. Test signals include generated documentation for the package and downstream use by allowed Hadoop-related projects.
