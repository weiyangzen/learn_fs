# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsContextIntegration.java

Purpose: static integration layer that owns thread-level IOStatistics enablement and maps current threads to contexts.

Important APIs, types, and functions: static configuration probe, `isIOStatisticsThreadLevelEnabled()`, `getCurrentIOStatisticsContext()`, `setThreadIOStatisticsContext()`, testing lookup by thread ID, `INSTANCE_ID`, and a `WeakReferenceThreadMap`.

Control flow: static initialization reads `IOSTATISTICS_THREAD_LEVEL_ENABLED` from a new `Configuration`. When enabled, current-thread lookup uses the weak reference thread map and creates `IOStatisticsContextImpl` instances on demand. When disabled, it returns the empty context. Setting null removes the current thread mapping.

State and persistence: process-wide static boolean, atomic ID generator, and weak references to contexts keyed by thread ID. No disk persistence.

Dependencies and integration points: depends on Hadoop configuration constants, `WeakReferenceThreadMap`, and context implementations. It backs the public static methods on `IOStatisticsContext`.

Risks and test signals: enablement is read during class initialization, so tests that change configuration must manage classloading or use test hooks. Weak references can disappear after GC. Tests should cover enabled/disabled modes, mapping replacement/removal, GC loss callbacks, unique IDs, and cross-thread isolation.
