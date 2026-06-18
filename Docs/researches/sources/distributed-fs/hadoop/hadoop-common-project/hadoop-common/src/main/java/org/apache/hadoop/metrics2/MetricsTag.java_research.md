## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsTag.java

Purpose: Immutable tag value object implementing `MetricsInfo`.

Important APIs/types/functions: Constructor stores `MetricsInfo` and string value. `name`, `description`, `value`, protected `info`, equality, hash, and `toString` provide metadata and value semantics.

Control flow: No complex flow; record builders and registries construct tags and records expose them.

State and persistence: Final metadata and value only; no persistence.

Dependencies/integration: Tags are used for context, hostname, source filters, record filtering, JMX tag attributes, and sink records.

Risks/test signals: Null metadata/value validation and equality behavior matter for filter maps and tests. Context tag value drives `MetricsRecordImpl.context()`.
