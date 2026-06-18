# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncher.java

Purpose: broad functional tests for `ServiceLauncher` success paths, launchable `execute()` behavior, exception mapping, shutdown hooks, constructor variants, and services that stop during startup.

Important APIs/types/functions: `ServiceLauncher.serviceMain`, `LaunchableService.execute`, `ServiceLaunchException`, `ServiceShutdownHook`, fixture services `RunningService`, `LaunchableRunningService`, `ExceptionInExecuteLaunchableService`, `NoArgsAllowedService`, `NullBindLaunchableService`, `InitInConstructorLaunchableService`, `StoppingInStartLaunchableService`, `StringConstructorOnlyService`, and `FailingStopInStartService`.

Control flow: tests call `assertRuns` or `assertLaunchOutcome` with fixture class names and arguments. Exception formatting tests construct `ServiceLaunchException` directly and inspect message/cause behavior. Shutdown-hook tests run hooks against null, normal, and stop-failing services.

State and persistence behavior: service state is in-memory. Some tests create config files via the base helper when verifying config arguments stripped from no-arg services.

Dependencies and integration points: exercises reflective service creation, constructor resolution, launchable argument binding, execute result-to-exit-code mapping, exception wrapping, and hook cleanup.

Risks and test signals: risks include wrong exit-code mapping, executing a service that already stopped in start, and hook failure leakage. Signals include exact launcher exit-code assertions, cause preservation checks, stopped-service assertions, and no-arg validation.
