# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailureTestService.java

Purpose: base fixture for launcher lifecycle failure tests.

Important APIs/types/functions: extends `BreakableService`; constructor parameters `failOnInit`, `failOnStart`, `failOnStop`, and `delay`; overrides `serviceStop`; overrides `createFailureException`; package-private `getExitCode`.

Control flow: inherits failure injection from `BreakableService`. `serviceStop` optionally sleeps before delegating, enabling interrupt timeout tests. `createFailureException` wraps lifecycle failures as `ServiceLaunchException(getExitCode(), toString())`.

State and persistence behavior: stores a final in-memory stop delay and uses `BreakableService` in-memory lifecycle/failure counters. No durable state.

Dependencies and integration points: used by specialized fail-in-constructor/init/start/stop fixtures and interrupt escalation tests.

Risks and test signals: centralizes exit-code behavior for launcher fixtures; changing it affects many launcher tests. Delay-based stop behavior is timing-sensitive but useful for forced shutdown timeout coverage.
