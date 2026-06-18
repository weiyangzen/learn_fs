# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncherCreationFailures.java

Purpose: defines negative tests for launcher creation and early lifecycle failures.

Important APIs/types/functions: `ServiceLauncher.serviceMain`, `assertServiceCreationFails`, `assertLaunchOutcome`, `LauncherExitCodes`, and fixture classes `FailInConstructorService`, `FailInInitService`, `FailInStartService`, and `FailingStopInStartService`.

Control flow: tests call the launcher with no arguments, an unknown class, a non-service class, a bad constructor class, and fixture services that fail during construction/init/start. Expected outcomes distinguish usage errors, service creation failures, and lifecycle failure exit codes.

State and persistence behavior: no durable state. Service instances are short-lived and generally fail before steady state.

Dependencies and integration points: covers reflective class loading, service type validation, constructor discovery, constructor exceptions, `ServiceLaunchException` exit-code propagation, and ignored stop failures during start.

Risks and test signals: failure cases are easy to conflate; this suite prevents all early failures being collapsed into a generic exit. Signals include specific creation-failure assertions and custom exit codes for init/start fixture failures.
