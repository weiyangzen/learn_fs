## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/SinkQueue.java

Purpose: Half-blocking circular queue for sink publication where producers never block and consumers block for data.

Important APIs/types/functions: `enqueue`, `consume`, `consumeAll`, `dequeue`, `front`, `back`, `clear`, `size`, and `capacity`. Nested `Consumer` callback consumes objects.

Control flow: `enqueue` returns false when full. Consumer operations enforce a single active consumer, wait for data, call the consumer outside some synchronized paths, then dequeue and clear the consumer lock. `clear` refuses while a consumer is active.

State and persistence: Fixed object array plus head, tail, size, and current consumer thread. In-memory only and synchronized around queue state.

Dependencies/integration: Used by `MetricsSinkAdapter` to buffer `MetricsBuffer` objects.

Risks/test signals: The circular index order, single-consumer guard, interrupt handling, and full-queue drop behavior are critical. Tests should cover capacity one, clear during consumption, and consumeAll order.
