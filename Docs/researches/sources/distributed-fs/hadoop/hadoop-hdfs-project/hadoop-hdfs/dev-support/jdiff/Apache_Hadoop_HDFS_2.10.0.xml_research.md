# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.10.0.xml

Purpose: `Apache_Hadoop_HDFS_2.10.0.xml` is a JDiff API baseline generated from Hadoop HDFS 2.10.0 public annotated APIs. It is used by API-difference tooling to compare HDFS public surface across releases.

Important structures: the root `api` element names `Apache Hadoop HDFS 2.10.0`, declares JDiff version `1.0.9`, references `api.xsd`, and includes a generated command-line comment showing doclet, classpath, source path, and dependency versions from the 2019 build environment. The file enumerates HDFS packages and selected public types.

API content: it includes the package documentation for `org.apache.hadoop.hdfs`, describing HDFS as a distributed `FileSystem` modeled loosely after GFS with a strict single-writer append stream model. It lists many packages such as `org.apache.hadoop.hdfs.protocol`, qjournal, datanode, namenode, tools, util, and web resources. Detailed public API entries shown include `JournalNodeMXBean.getJournalsStatus()`, the `AuditLogger` interface and its `initialize()`/`logAuditEvent()` methods, `HdfsAuditLogger` overloads, and `INodeAttributeProvider` methods for startup, shutdown, attribute lookup, and external access-control enforcer customization.

Control flow and integration behavior: this XML is not runtime code. It is an input to JDiff/reporting tasks that parse packages, classes, interfaces, methods, params, docs, visibility, abstract/static/final flags, and deprecation state to detect incompatible public API changes.

Dependencies and persistence behavior: the generated command line captures a Java 7-era build, Hadoop 2.10.0 artifacts, ZooKeeper 3.4.9, Curator 2.7.1, Guava 11.0.2, Jackson 2.7.x/1.9.x components, and other dependencies. These details document the build context for the baseline but are not API entries themselves.

Risks and test signals: hand-editing this file can corrupt API compatibility checks. The main signal is a stable public HDFS baseline for 2.10.0; changes to downstream JDiff comparisons should be interpreted as API drift from this baseline, not as executable test behavior.
