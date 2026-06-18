# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetSpaceUsed.java

Purpose: validates `CachingGetSpaceUsed.Builder` and `GetSpaceUsed.Builder` construction paths for Hadoop local disk-usage measurement. It checks class selection from configuration, explicit class injection, initial used-space propagation, refresh interval propagation, and non-caching implementations.

Important APIs/types/functions: `CachingGetSpaceUsed.Builder`, `GetSpaceUsed`, `CachingGetSpaceUsed`, configuration key `fs.getspaceused.classname`, and test-only `DummyDU`/`DummyGetSpaceUsed`. `setPath`, `setInterval`, `setInitialUsed`, `setConf`, `setKlass`, `build`, `getUsed`, `getRefreshInterval`, and `running` are the exercised API surface.

Control flow/state/persistence: each test creates a fresh temp directory under `GenericTestUtils.getTestDir("TestGetSpaceUsed")`, deletes it in setup/teardown, creates a file, builds a disk-usage object, asserts properties, and closes caching instances. `DummyDU.refresh()` is intentionally a no-op so tests isolate builder state from real `du` execution. The only persistent state is temporary filesystem content removed after each test.

Dependencies/integration points: integrates with Hadoop `Configuration`, `FileUtil`, local `File`, JUnit lifecycle annotations, and the disk-usage builder reflection path. It indirectly guards production subclasses that rely on builder constructors.

Risks/test signals: reflection-based constructor failures, ignored configuration class names, accidental background refresh thread startup at interval zero, and regressions where non-caching implementations are forced through `CachingGetSpaceUsed` assumptions. Strong signal comes from asserting concrete class type, initial value, interval, and non-running state.
