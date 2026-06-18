<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/WriteObjectFlags.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/WriteObjectFlags.java

Purpose: enum of S3A object-write feature flags used both for builder option parsing and output stream `hasCapability()` probes.

Important APIs/types/functions: flags include `ConditionalOverwrite`, `ConditionalOverwriteEtag`, `CreateMultipart`, `Performance`, and non-configurable `Recursive`. Each flag stores its configuration/capability key. `isEnabled(Configuration)` reads a boolean key defaulting false. `hasKey(String)` matches non-empty keys.

Control flow: create-file/build paths can map option keys to enum values and probe booleans; output streams can expose the same key namespace as capabilities.

State/persistence: enum constants are static process state only. No persistence.

Dependencies/integration: depends on Hadoop create-file option keys and S3A constants for multipart/performance behavior.

Risks/test signals: `Recursive` has an empty key, so `isEnabled()` on it always reads an empty config key and should not be used for configurable options. Tests should assert key matching, disabled defaults, and capability names for conditional overwrite and multipart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/write/WriteObjectFlags.java -->
