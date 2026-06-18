# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/package-info.java

Purpose: package-level documentation and annotations for raw erasure coders.

Important APIs/types/functions: package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

Control flow: documentation explains that raw erasure coders are low-level math components used by higher-level erasure coders, operating on groups of byte buffers/chunks rather than block-group layout.

State and persistence: none.

Dependencies and integration: imports Hadoop classification annotations and applies them to `org.apache.hadoop.io.erasurecode.rawcoder`.

Risks: signals non-public, unstable API; external use should not rely on compatibility. Tests are not direct, but release checks should ensure package annotations remain aligned with intended API stability.
