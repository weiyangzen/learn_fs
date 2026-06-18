# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/AsyncDiskService.java

Purpose: `AsyncDiskService` manages one thread pool per storage volume for asynchronous disk work such as background deletion.

Important APIs and types: constructor accepts volume roots. `execute(root, task)` submits to a root-specific executor. `shutdown`, `awaitTermination`, and `shutdownNow` manage all executors.

Control flow: construction creates a `ThreadPoolExecutor` per volume with core size 1, max 4, unbounded queue, 60-second keepalive, core thread timeout, and `SubjectInheritingThread`s in a shared thread group. `execute` synchronizes lookup and submission. Graceful shutdown iterates all executors; `awaitTermination` shares a total deadline across them; `shutdownNow` aggregates pending tasks.

State and persistence behavior: in-memory map from root string to executor plus thread factory/group. No disk state is modified directly by this class; tasks perform the actual IO.

Dependencies and integration points: used by HDFS/MapReduce disk cleanup code; depends on `SubjectInheritingThread`, `Time`, Java executors, and SLF4J.

Risks: unbounded queues can grow under heavy deletion backlogs. Unknown roots throw `RuntimeException`. Methods are synchronized, so a long `awaitTermination` blocks submissions/shutdown calls. Duplicate volume strings replace prior executor in the map.

Test signals: cover per-volume routing, unknown root failure, task execution, graceful timeout, immediate shutdown returning pending tasks, subject inheritance, duplicate volume behavior, and core-thread timeout.
