# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryptionHandler.java

Purpose: Unit-tests `ReencryptionHandler` throttling behavior independent of a real NameNode. It verifies configured handler lock-time ratio, invalid throttle configuration rejection, and backpressure when too many reencryption tasks accumulate.

Important APIs and functions: `mockReencryptionhandler()` builds a real `ReencryptionHandler` around mocked `EncryptionZoneManager`, `FSDirectory`, and `FSNamesystem`, with a JKS-backed `KeyProviderCryptoExtension`. Tests use Mockito `StopWatch` mocks and Whitebox to set `throttleTimerAll`, `throttleTimerLocked`, `taskQueue`, and `submissions`.

Control flow: `testThrottle` simulates 30s total elapsed and 20s locked time with ratio 0.5, expecting sleep long enough to reduce locked-time share. `testThrottleNoOp` simulates lower locked time and expects no sleep. `testThrottleConfigs` validates non-positive ratios throw. `testThrottleAccumulatingTasks` fills a `ZoneSubmissionTracker` above processor-count threshold, clears it from another thread after 3s, and verifies throttle waits.

State and persistence behavior: No HDFS persistent state exists. Mutable state is internal handler throttling timers, a blocking task queue, and the submissions map tracking futures per zone.

Dependencies and integration points: Depends on KMS utility provider creation, `JavaKeyStoreProvider`, `KeyProviderCryptoExtension`, `ReencryptionUpdater.ZoneSubmissionTracker`, `SubjectInheritingThread`, Mockito, Whitebox, and the config key `DFS_NAMENODE_REENCRYPT_THROTTLE_LIMIT_HANDLER_RATIO_KEY`.

Risks: Wall-clock sleep assertions are inherently flaky on overloaded systems. Whitebox mutation ties the tests to private field names. The throttle ratio math must avoid negative/zero configuration and avoid deadlock when task futures pile up.

Test signals: Passing signals are measured sleep windows, sub-second no-op throttle, expected `IllegalArgumentException` content for invalid config, and waiting until accumulated tasks are cleared.
