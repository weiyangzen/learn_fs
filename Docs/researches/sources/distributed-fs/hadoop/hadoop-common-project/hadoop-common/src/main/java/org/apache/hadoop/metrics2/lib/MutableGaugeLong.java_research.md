## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeLong.java

Purpose: Mutable long gauge.

Important APIs/types/functions: Provides long set/increment/decrement operations, `value`, and snapshot as a long gauge.

Control flow: Mutations mark changed; snapshot writes only if all or changed and then clears changed.

State and persistence: In-memory long value.

Dependencies/integration: Registry and annotations create it for long-valued instantaneous metrics.

Risks/test signals: Tests should cover large values, negative values, and changed tracking.
