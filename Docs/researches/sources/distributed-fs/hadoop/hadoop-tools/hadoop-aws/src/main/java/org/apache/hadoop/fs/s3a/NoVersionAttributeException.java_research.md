# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/NoVersionAttributeException.java

Purpose: public unstable path exception indicating that an S3 object lacks the version attribute required by the configured change-detection policy.

Important APIs/types: extends `PathIOException`; constructor accepts path and detail message.

Control flow: thrown by change-detection logic when version IDs are required but absent.

State and persistence behavior: stores path, operation/message fields through `PathIOException`; no persistence.

Dependencies and integration points: integrates S3A change detection with Hadoop path-based IO exception reporting.

Risks: only applies when version-based detection is required; using it when versioning is optional would over-fail reads.

Test signals: change-detection tests should assert this exception when version ID is missing under require-version mode.
