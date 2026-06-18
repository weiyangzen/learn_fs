# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/package-info.java

Purpose: package metadata for private/unstable filesystem store support classes.

Important APIs, types, and functions: applies Hadoop private/unstable annotations to `org.apache.hadoop.fs.store`.

Control flow: no executable flow.

State and persistence: no runtime state.

Dependencies and integration points: depends on Hadoop classification annotations. It covers helpers such as upload data blocks, ETag checksums, and logging utilities used by object-store filesystems.

Risks and test signals: package annotation changes affect API compatibility expectations. Test signal is documentation/source generation preserving private unstable classification.
