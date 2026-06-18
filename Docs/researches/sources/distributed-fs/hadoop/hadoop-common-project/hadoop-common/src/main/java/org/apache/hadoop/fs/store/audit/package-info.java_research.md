# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/package-info.java

Purpose: package metadata for unstable private store audit support APIs.

Important APIs, types, and functions: applies Hadoop private/unstable annotations to `org.apache.hadoop.fs.store.audit`.

Control flow: no executable flow.

State and persistence: no runtime state.

Dependencies and integration points: depends on Hadoop classification annotations. It frames the audit API as internal support for filesystem/store implementations.

Risks and test signals: compatibility expectations are lower than public APIs, but downstream stores may still depend on them. Test signal is javadoc/source generation with the intended annotations.
