# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/package-info.java

Purpose: Declares package-level documentation and stability annotations for `org.apache.hadoop.fs.viewfs`, identifying it as the package for `ViewFileSystem` and `ViewFileSystemOverloadScheme` classes.

Important APIs and types: Provides package annotations `@InterfaceAudience.LimitedPrivate({"MapReduce", "HBase", "Hive" })` and `@InterfaceStability.Stable`. It exports no runtime classes or functions itself.

Control flow: None. The file only affects package metadata and generated documentation.

State and persistence: No state or persistence.

Dependencies and integration points: Imports Hadoop classification annotations. Tooling, downstream consumers, and generated Javadocs use these package annotations to understand intended audience and compatibility expectations.

Risks: Package-level stability communicates compatibility promises. Changing these annotations affects downstream expectations even though runtime behavior is unchanged.

Test signals: Compile and Javadoc generation are the relevant checks; functional tests are unnecessary for this metadata-only file.
