## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeInt.java

Purpose: Mutable integer gauge.

Important APIs/types/functions: Provides `incr`, `incr(int)`, `decr`, `decr(int)`, `set(int)`, `value`, and `snapshot`.

Control flow: Mutations update the value and mark changed; snapshot emits an int gauge when needed.

State and persistence: In-memory int and changed flag.

Dependencies/integration: Used for queue size and application gauges.

Risks/test signals: Tests should cover negative values, repeated snapshots with `all=false`, and all mutation overloads.
