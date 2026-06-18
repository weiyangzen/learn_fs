## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounterLong.java

Purpose: Mutable long counter for high-volume counts.

Important APIs/types/functions: Supports `incr()`, `incr(long)`, `value()`, and `snapshot`.

Control flow: Increment marks changed; snapshot emits a long counter when requested or changed and clears the flag.

State and persistence: In-memory long value and changed flag.

Dependencies/integration: Used for dropped publish counts and application metrics via registry/annotations.

Risks/test signals: Tests should cover long values, snapshot changed semantics, and thread-safety expectations.
