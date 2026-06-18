# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/package-info.java

Purpose: package documentation and classification for Hadoop's BZip2 compression/decompression implementation.

Important APIs and control flow: it declares no executable code; it marks the package `@InterfaceAudience.Private` and `@InterfaceStability.Unstable` and documents that the package implements the BZip2 algorithm.

State and persistence: no runtime state. The annotations are compile-time/source-level API signals.

Dependencies and integration: imports Hadoop classification annotations and scopes BZip2 classes under `org.apache.hadoop.io.compress.bzip2`, integrating with Hadoop compression codecs outside this file.

Risks and test signals: no direct unit tests are needed beyond checking Javadoc/annotation compilation. Any public exposure changes should be reviewed because the package is explicitly private and unstable.
