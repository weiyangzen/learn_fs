# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/package-info.java

Purpose: package-level documentation and annotations for raw erasure coder utility classes.

Important APIs/types/functions: package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

Control flow: no runtime logic; comment identifies the package as general helpers for raw erasure coder implementations.

State and persistence: none.

Dependencies and integration: imports Hadoop classification annotations and applies them to `org.apache.hadoop.io.erasurecode.rawcoder.util`.

Risks: the utilities are explicitly private/unstable, so external consumers should not depend on compatibility. Test signals are indirect through coders and package annotation checks if API surface is audited.
