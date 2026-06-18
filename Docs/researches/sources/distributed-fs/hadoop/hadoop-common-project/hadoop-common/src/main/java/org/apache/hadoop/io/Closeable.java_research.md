<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Closeable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Closeable.java

Purpose: deprecated Hadoop alias for `java.io.Closeable`.

Important APIs, types, and functions: the interface extends `java.io.Closeable` and adds no methods.

Control flow: no control flow.

State and persistence: no state.

Dependencies and integration points: retained for source and binary compatibility with older Hadoop APIs.

Risks and test signals: low runtime risk. Compatibility tests should ensure old code compiling against `org.apache.hadoop.io.Closeable` still works while new code can use `java.io.Closeable` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Closeable.java -->
