# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailingStopInStartService.java

Purpose: fixture service that stops itself during start while its stop operation is configured to fail.

Important APIs/types/functions: extends `FailureTestService`; constants `NAME` and `EXIT_CODE = -4`; constructor sets `failOnStop=true`; `serviceStart` calls `super.serviceStart()` and then `stop()` inside a swallowed catch; overrides `getExitCode`.

Control flow: start completes enough to invoke stop. Stop failure is intentionally caught inside the fixture, allowing launcher tests to check that this edge path can still be treated as a successful run in some launcher scenarios and as recorded failure in direct service tests.

State and persistence behavior: service state and failure cause are in-memory. No persistence.

Dependencies and integration points: integrates with `BreakableService` failure injection and launcher stop-in-start behavior tests.

Risks and test signals: covers a subtle case where stop failure during startup could either abort startup or be ignored. Test signals include stopped-state and failure-cause assertions in callers.
