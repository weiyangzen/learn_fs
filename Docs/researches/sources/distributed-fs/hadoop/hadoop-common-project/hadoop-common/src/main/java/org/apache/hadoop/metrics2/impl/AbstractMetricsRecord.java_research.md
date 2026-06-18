## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/AbstractMetricsRecord.java

Purpose: Partial `MetricsRecord` implementation that centralizes equality, hashing, and string rendering for concrete records.

Important APIs/types/functions: Implements `equals` by comparing timestamp, name, description, tags, and metric elements. Implements `hashCode` from name, description, and tags, and `toString` with timestamp, metadata, tags, and metrics.

Control flow: Concrete records provide all `MetricsRecord` accessors; the abstract base calls those accessors when comparing or rendering.

State and persistence: Stateless abstract base; all record state lives in concrete subclasses or wrappers.

Dependencies/integration: Base for `MetricsRecordImpl` and filtered record wrappers.

Risks/test signals: `hashCode` intentionally omits timestamp and metrics despite `equals` including them, which is legal but can increase hash collisions. Tests should cover equality for metric iterable contents and toString rendering.
