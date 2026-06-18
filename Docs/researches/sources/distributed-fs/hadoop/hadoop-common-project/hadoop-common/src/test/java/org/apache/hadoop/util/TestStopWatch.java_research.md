# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStopWatch.java

Purpose: tests `StopWatch`, a closeable timing helper with explicit running-state transitions.

Important APIs and types: `StopWatch.start`, `stop`, `reset`, `isRunning`, and `AutoCloseable.close` through try-with-resources.

Control flow: `testStartAndStop` verifies a new watch is not running, becomes running after `start`, and stops after `stop`. `testStopInTryWithResource` creates a watch in try-with-resources and expects no exception on close without start. `testExceptions` verifies stopping before start and starting twice both throw `IllegalStateException`.

State and persistence: state is in-memory start/running fields. No external dependencies beyond JUnit.

Dependencies and integration points: utility is used by code paths that need scoped duration measurement.

Risks: invalid state transitions can hide timing bugs or throw in cleanup blocks. Test signals are running-state assertions and caught exception-type checks.
