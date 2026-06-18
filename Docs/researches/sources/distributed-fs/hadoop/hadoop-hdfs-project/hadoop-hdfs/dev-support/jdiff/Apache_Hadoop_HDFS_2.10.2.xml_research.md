# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.10.2.xml

Purpose: `Apache_Hadoop_HDFS_2.10.2.xml` is the JDiff API baseline for Hadoop HDFS 2.10.2. It mirrors the 2.10.0 baseline structure while recording a newer generated date, release name, build paths, and dependency set.

Important structures: the root `api` element names `Apache Hadoop HDFS 2.10.2`, uses JDiff version `1.0.9`, references `api.xsd`, and contains a generated command-line comment from a 2022 build environment. The package/type/method content visible in the file is structurally the same as the 2.10.0 baseline in this subset.

API content: it preserves the `org.apache.hadoop.hdfs` package documentation about the distributed filesystem and single-writer ordered byte-stream model. It lists the same HDFS package families and includes public entries for `JournalNodeMXBean`, `AuditLogger`, `HdfsAuditLogger`, and `INodeAttributeProvider`, with method signatures, parameter types, visibility, and documentation blocks used by API comparison tooling.

Control flow and integration behavior: like the 2.10.0 file, this is a generated static API description consumed by JDiff/report tasks. It does not run in tests, but it anchors release-to-release compatibility analysis for the HDFS module.

Dependencies and version context: the command-line comment records updated build dependencies relative to 2.10.0, including newer SLF4J, HTTP components, Nimbus JOSE JWT, ZooKeeper 3.4.14, Curator 2.13.0, commons-compress, Woodstox, Netty, Jackson databind 2.9.10.7, reload4j bindings, SpotBugs annotations, and Yetus audience annotations. These are build-context differences rather than direct API entries.

Risks and test signals: the file should remain generated and source-controlled as a release baseline. The visible diff from 2.10.0 is mostly metadata and build classpath information, while the represented public API in this subset remains stable; that is the key compatibility signal.
