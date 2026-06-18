# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInStartService.java

Purpose: fixture service that fails during start and reports a distinctive exit code.

Important APIs/types/functions: extends `FailureTestService`; constants `NAME` and `EXIT_CODE = -2`; constructor configures `failOnStart=true`; overrides `getExitCode`.

Control flow: launcher construction and init succeed; start raises a `ServiceLaunchException` produced by the base fixture's failure factory. Tests assert the launcher surfaces `-2`.

State and persistence behavior: all state is lifecycle failure state on the service instance. No persistence.

Dependencies and integration points: used by `TestServiceLauncherCreationFailures` for start-failure classification.

Risks and test signals: protects launcher rollback/start failure mapping. Narrow fixture but high signal for lifecycle phase attribution.
