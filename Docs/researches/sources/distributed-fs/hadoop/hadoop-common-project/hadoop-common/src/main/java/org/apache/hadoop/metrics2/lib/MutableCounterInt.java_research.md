## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounterInt.java

Purpose: Mutable integer counter.

Important APIs/types/functions: Constructor accepts `MetricsInfo` and initial value. `incr()` and `incr(int)` advance the count. `value()` exposes current value. `snapshot` emits an int counter when all or changed.

Control flow: Increment methods update value and set changed; snapshot clears changed after writing.

State and persistence: In-memory int value plus inherited changed flag; synchronized where needed.

Dependencies/integration: Created by registry and annotation factory; emitted through `MetricsRecordBuilder.addCounter`.

Risks/test signals: Integer overflow is possible if counts exceed int range. Tests should cover initial value, increments, `all=false`, and `all=true`.
