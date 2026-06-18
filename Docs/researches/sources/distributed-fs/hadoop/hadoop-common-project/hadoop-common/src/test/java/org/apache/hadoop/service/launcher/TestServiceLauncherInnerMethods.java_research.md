# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncherInnerMethods.java

Purpose: tests lower-level `ServiceLauncher` methods without always going through the CLI wrapper.

Important APIs/types/functions: `launchService`, `launchExpectingException`, `getService`, `getServiceException`, `loadConfigurationClasses`, and fixtures `NoArgsAllowedService`, `LaunchableRunningService`, `ExceptionInExecuteLaunchableService`, and `BreakableService`.

Control flow: tests launch services directly, retrieve the created service, assert lifecycle state, invoke `execute()` manually for a launchable service, and validate expected launch exceptions. The config-loading test creates a launcher by short service name and checks configuration class loading creates exactly one configured class after discovering more than one class name candidate.

State and persistence behavior: service state is in-memory. No file writes occur in this file.

Dependencies and integration points: targets `ServiceLauncher` internals used by higher-level CLI flows, especially access to the launched service and configuration class resolution.

Risks and test signals: risks include hidden launcher regressions masked by `serviceMain`, wrong remaining-argument handling, and failing to expose the launched service. Signals include state assertions, direct execute return-code assertion, and throwable-to-exit-code validation.
