# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/RunningService.java

Purpose: simple asynchronous service fixture for launcher tests of non-launchable services that run in a background thread and stop themselves.

Important APIs/types/functions: extends `AbstractService` and implements `Runnable`; constants `NAME`, `DELAY`, `DELAY_TIME`, `FAIL_IN_RUN`, and `FAILURE_MESSAGE`; methods `serviceInit`, `serviceStart`, `run`, and `isInterrupted`.

Control flow: `serviceInit` reads delay and failure flags from configuration. `serviceStart` starts a `SubjectInheritingThread` named after the service. `run` sleeps, optionally records a failure via `noteFailure`, catches interruption, and stops the service.

State and persistence behavior: in-memory fields `delayTime`, `failInRun`, and `interrupted`; configuration seeds runtime behavior. No persistence.

Dependencies and integration points: used by launcher tests for simple service execution, config propagation, failure recording, and wait-for-stop behavior.

Risks and test signals: asynchronous timing can be flaky if delays are too short or threads leak. It provides strong signal for launcher wait behavior and service self-stop handling.
