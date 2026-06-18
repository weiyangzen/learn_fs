# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInInitService.java

Purpose: fixture service that fails in init and reports a distinctive exit code.

Important APIs/types/functions: extends `FailureTestService`; constants `NAME` and `EXIT_CODE = -1`; constructor configures `failOnInit=true`; overrides package-private `getExitCode`.

Control flow: launcher creates the service successfully, then `BreakableService` init fails. `FailureTestService.createFailureException` converts the lifecycle failure into `ServiceLaunchException(EXIT_CODE, toString())`.

State and persistence behavior: service state moves into failure/stop handling in memory; no persistent state.

Dependencies and integration points: used by launcher creation-failure tests to distinguish init failure from constructor failure.

Risks and test signals: ensures lifecycle exceptions carry service-specific exit codes. The signal depends on `BreakableService` invoking `createFailureException`.
