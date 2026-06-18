# subset-b-007406 Research

Grouped research report for Hadoop service lifecycle, service launcher, launcher test fixtures, and shared Hadoop test utilities. Each section preserves the source path and is wrapped for reconciliation into the source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestCompositeService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestCompositeService.java

Purpose: this JUnit 5 test suite validates `CompositeService` behavior around child ordering, failure rollback, stop policy, and dynamic service insertion. It is a behavioral contract for Hadoop services that aggregate child services.

Important APIs/types/functions: `CompositeService`, `Service.STATE`, `BreakableService`, `ServiceStateException`, local `ServiceManager`, `CompositeServiceImpl`, `CompositeServiceAddingAChild`, and `AddSiblingService`. `CompositeServiceImpl` records lifecycle call order and can throw on start/stop; `ServiceManager` exposes protected `addService`; `AddSiblingService` injects another service when its own state matches a trigger.

Control flow: baseline tests initialize, start, and stop five children, asserting init/start execute in registration order while stop executes in reverse order. Failure tests force a child start or stop exception and verify rollback/stop semantics. The long matrix adds children or siblings before init, during init/start/stop, and with child states `NOTINITED`, `INITED`, `STARTED`, or `STOPPED`, asserting which additions are managed, rejected, or left untouched.

State and persistence behavior: all state is in-memory service lifecycle state plus static call counters reset before each test. There is no persistence. The static `STOP_ONLY_STARTED_SERVICES` mirrors the implementation policy and changes expected stop behavior from `INITED`.

Dependencies and integration points: integrates directly with Hadoop service primitives and JUnit timeouts. It is a regression suite for `CompositeService.addService`, `addIfService`, `removeService`, parent lifecycle traversal, and exception-safe stop behavior.

Risks and test signals: the test matrix is broad but has fragile expectations tied to current stop policy and lifecycle side effects. Strong signals include explicit order counters, state assertions after every transition, reverse-stop verification, duplicate-stop no-op behavior, dynamic-add race coverage via timeouts, and exception rollback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestCompositeService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestGlobalStateChangeListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestGlobalStateChangeListener.java

Purpose: verifies process-wide `AbstractService` global listener registration, de-registration, event dispatch ordering, and failure isolation semantics.

Important APIs/types/functions: `AbstractService.registerGlobalListener`, `AbstractService.unregisterGlobalListener`, `AbstractService.resetGlobalListeners`, `ServiceStateChangeListener`, `BreakableStateChangeListener`, `LoggingStateChangeListener`, and `BreakableService`. Helper methods wrap register/unregister and assert listener last-state/event-count fields.

Control flow: each test creates services and global listeners, drives `init/start/stop`, then checks listener observations. Double registration must collapse to one registration. Chain tests register several listeners, make one fail on `STARTED`, and verify earlier listeners see the transition while later listeners are skipped for that failing notification.

State and persistence behavior: global listener state is static process state and is reset in `@AfterEach`, which is essential to avoid cross-test contamination. Listener event counters, failure counters, and last-service references are in-memory only.

Dependencies and integration points: exercises global notification hooks in `AbstractService`, including interaction with local `BreakableService` state transitions and listener exceptions.

Risks and test signals: risks are shared static state and listener failure short-circuiting. Test signals include cleanup after every test, assertions that service state changes complete before listener failures surface, and verification that unregister order does not matter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestGlobalStateChangeListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestServiceLifecycle.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestServiceLifecycle.java

Purpose: validates core `AbstractService` lifecycle contracts: idempotent transitions, failure recording, listener notification, self-terminating services, and unusual transitions invoked inside lifecycle callbacks.

Important APIs/types/functions: `BreakableService`, `BreakableStateChangeListener`, `LoggingStateChangeListener`, `ServiceStateChangeListener`, `SubjectInheritingThread`, and local helper services `AsyncSelfTerminatingService`, `SelfTerminatingService`, `StartInInitService`, and `StopInInitService`.

Control flow: tests walk `NOTINITED -> INITED -> STARTED -> STOPPED`, then repeat `init/start/stop` to assert idempotence. Failure paths force exceptions in init, start, or stop and check final state, failure cause, and failure state. Listener tests register, unregister, self-unregister, and fail listeners while services transition. Async tests start a service thread that stops itself and wakes a waiting listener.

State and persistence behavior: state is the `AbstractService` in-memory lifecycle state, counters in `BreakableService`, listener event counts, failure cause/state, and short-lived thread state. No filesystem or durable state is used.

Dependencies and integration points: this is a direct integration test of Hadoop's service model and notification mechanics. It also exercises subject-inheriting thread startup for asynchronous stop behavior.

Risks and test signals: risk areas are re-entrant lifecycle calls (`start()`/`stop()` from `serviceInit` or `serviceStart`), listener mutation during callback, and failure propagation. Signals are explicit state-count assertions, event-count checks, wait/notify verification, and failure-cause validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestServiceLifecycle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestServiceOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestServiceOperations.java

Purpose: tests the quiet stop utility path when `Service.stop()` itself throws, ensuring logging and stack trace handling occur instead of rethrowing.

Important APIs/types/functions: `ServiceOperations.stopQuietly(Logger, Service)`, Mockito mocks for `Service` and `RuntimeException`, `GenericTestUtils.LogCapturer.captureLogs`, and AssertJ string assertions.

Control flow: the mocked service is configured to throw a mocked runtime exception from `stop()`. `stopQuietly` is invoked with a test logger. The test then inspects captured log output and verifies the exception's `printStackTrace(PrintWriter)` was called once.

State and persistence behavior: all state is in-memory mock invocation state and the temporary log-capture buffer. No durable state is written.

Dependencies and integration points: integrates `ServiceOperations` with SLF4J/log4j capture and Mockito. It guards the operational behavior expected by teardown code across service tests and production utility use.

Risks and test signals: the main risk is swallowing stop failures without diagnostic detail. The test signal is narrow but precise: a failure message naming the service is logged and stack trace rendering is requested exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/TestServiceOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/AbstractServiceLauncherTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/AbstractServiceLauncherTestBase.java

Purpose: shared base for service launcher tests. It disables real JVM exits, provides launch/assert helpers, creates temporary XML configs, and stops launched services after each test.

Important APIs/types/functions: `LauncherExitCodes`, `ExitUtil.disableSystemExit/disableSystemHalt`, `ServiceLauncher.serviceMain`, `ServiceLauncher.launchService`, `ServiceLaunchException`, `ServiceOperations.stopQuietly`, `failf/failif`, `configFile`, `newConf`, `assertLaunchOutcome`, and `launchExpectingException`.

Control flow: `@BeforeAll` converts exits/halts into exceptions; `@BeforeEach` names the test thread; `@AfterEach` quietly stops any service registered via `setServiceToTeardown`. Launch helpers either call the CLI entry point or construct `ServiceLauncher`, then assert exit code and expected exception text.

State and persistence behavior: holds one in-memory teardown service reference. Configuration files are persisted under `target/launcher/conf` for command-line config tests.

Dependencies and integration points: centralizes interaction between JUnit tests and the launcher, ExitUtil, configuration XML writing, and service lifecycle cleanup.

Risks and test signals: incorrect exit disabling would terminate the test JVM. The base reduces that risk and standardizes assertions. Config file creation under `target` is intentional but can leave test artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/AbstractServiceLauncherTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/ExitTrackingServiceLauncher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/ExitTrackingServiceLauncher.java

Purpose: test subclass of `ServiceLauncher` that records the exit exception while still delegating to the normal exit path.

Important APIs/types/functions: generic `ExitTrackingServiceLauncher<S extends Service>`, overridden `exit(ExitUtil.ExitException)`, overridden `exit(int, String)`, public `bindCommandOptions`, and `getExitException`.

Control flow: tests instantiate the launcher with a service class name, then normal launcher code eventually calls `exit`. This subclass stores the exception in `exitException` before delegating to `super.exit`, and wraps integer/message exits as `ServiceLaunchException`.

State and persistence behavior: one in-memory `ExitException` field records the last exit. There is no filesystem state.

Dependencies and integration points: depends on the test base disabling system exits. It exposes protected command option binding so command extraction can be tested directly.

Risks and test signals: useful for tests that need to assert exit details without losing normal launcher behavior. Risk is that calling `super.exit` still raises if `ExitUtil` is not disabled, so it is tied to the base class setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/ExitTrackingServiceLauncher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceConf.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceConf.java

Purpose: verifies launcher command-line configuration file handling and propagation into simple and launchable services.

Important APIs/types/functions: `LauncherArguments.ARG_CONF_PREFIXED`, `ServiceLauncher.extractCommandOptions`, `ExitTrackingServiceLauncher`, `Configuration`, `RunningService`, `LaunchableRunningService`, `configFile`, and `newConf`.

Control flow: tests launch services with and without `--conf` arguments, including missing file, unbalanced flag, multiple config files, and malformed XML content. Low-level extraction tests call `bindCommandOptions` and `extractCommandOptions` directly, asserting remaining args and loaded properties.

State and persistence behavior: temporary Hadoop XML configuration files are written under `target/launcher/conf`. Loaded configuration values control `failInRun` and exit-code properties in fixture services.

Dependencies and integration points: covers command parsing, config XML loading, property precedence, `LaunchableService.bindArgs`, and `RunningService.serviceInit`.

Risks and test signals: risks include silently dropping config files, accepting malformed command lines, or losing properties when `bindArgs` returns a new config. Signals include expected command argument errors, propagated failure flags, dual-file merge checks, and malformed file rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceInterruptHandling.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceInterruptHandling.java

Purpose: tests signal/interrupt handling for the service launcher, including signal registration, first-interrupt shutdown, second-interrupt halt escalation, and forced-shutdown timeout detection.

Important APIs/types/functions: `IrqHandler`, `IrqHandler.Interrupted`, `IrqHandler.InterruptData`, `InterruptEscalator`, `ExitTrackingServiceLauncher`, `ExitUtil.ExitException`, `ExitUtil.HaltException`, `BreakableService`, `FailureTestService`, and `GenericTestUtils.waitFor`.

Control flow: `testRegisterAndRaise` binds a handler for `USR2`, raises it, waits asynchronously, and asserts signal count and data. Escalation tests call `InterruptEscalator.interrupted` directly: first call stops the service and exits; second call halts. A delayed `FailureTestService` stop path verifies timeout tracking.

State and persistence behavior: state is in-memory signal count, captured interrupt data, launcher service reference, and escalator flags. No durable state.

Dependencies and integration points: integrates launcher shutdown paths with Unix-style signal handling abstractions and `ExitUtil` halt/exit conversion.

Risks and test signals: risks are platform/signal flakiness and slow service stops. Signals include async wait, explicit exit-code assertions, stopped-service assertions, second-signal halt detection, and timeout flag validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceInterruptHandling.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncher.java

Purpose: broad functional tests for `ServiceLauncher` success paths, launchable `execute()` behavior, exception mapping, shutdown hooks, constructor variants, and services that stop during startup.

Important APIs/types/functions: `ServiceLauncher.serviceMain`, `LaunchableService.execute`, `ServiceLaunchException`, `ServiceShutdownHook`, fixture services `RunningService`, `LaunchableRunningService`, `ExceptionInExecuteLaunchableService`, `NoArgsAllowedService`, `NullBindLaunchableService`, `InitInConstructorLaunchableService`, `StoppingInStartLaunchableService`, `StringConstructorOnlyService`, and `FailingStopInStartService`.

Control flow: tests call `assertRuns` or `assertLaunchOutcome` with fixture class names and arguments. Exception formatting tests construct `ServiceLaunchException` directly and inspect message/cause behavior. Shutdown-hook tests run hooks against null, normal, and stop-failing services.

State and persistence behavior: service state is in-memory. Some tests create config files via the base helper when verifying config arguments stripped from no-arg services.

Dependencies and integration points: exercises reflective service creation, constructor resolution, launchable argument binding, execute result-to-exit-code mapping, exception wrapping, and hook cleanup.

Risks and test signals: risks include wrong exit-code mapping, executing a service that already stopped in start, and hook failure leakage. Signals include exact launcher exit-code assertions, cause preservation checks, stopped-service assertions, and no-arg validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncherCreationFailures.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncherCreationFailures.java

Purpose: defines negative tests for launcher creation and early lifecycle failures.

Important APIs/types/functions: `ServiceLauncher.serviceMain`, `assertServiceCreationFails`, `assertLaunchOutcome`, `LauncherExitCodes`, and fixture classes `FailInConstructorService`, `FailInInitService`, `FailInStartService`, and `FailingStopInStartService`.

Control flow: tests call the launcher with no arguments, an unknown class, a non-service class, a bad constructor class, and fixture services that fail during construction/init/start. Expected outcomes distinguish usage errors, service creation failures, and lifecycle failure exit codes.

State and persistence behavior: no durable state. Service instances are short-lived and generally fail before steady state.

Dependencies and integration points: covers reflective class loading, service type validation, constructor discovery, constructor exceptions, `ServiceLaunchException` exit-code propagation, and ignored stop failures during start.

Risks and test signals: failure cases are easy to conflate; this suite prevents all early failures being collapsed into a generic exit. Signals include specific creation-failure assertions and custom exit codes for init/start fixture failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncherCreationFailures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncherInnerMethods.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncherInnerMethods.java

Purpose: tests lower-level `ServiceLauncher` methods without always going through the CLI wrapper.

Important APIs/types/functions: `launchService`, `launchExpectingException`, `getService`, `getServiceException`, `loadConfigurationClasses`, and fixtures `NoArgsAllowedService`, `LaunchableRunningService`, `ExceptionInExecuteLaunchableService`, and `BreakableService`.

Control flow: tests launch services directly, retrieve the created service, assert lifecycle state, invoke `execute()` manually for a launchable service, and validate expected launch exceptions. The config-loading test creates a launcher by short service name and checks configuration class loading creates exactly one configured class after discovering more than one class name candidate.

State and persistence behavior: service state is in-memory. No file writes occur in this file.

Dependencies and integration points: targets `ServiceLauncher` internals used by higher-level CLI flows, especially access to the launched service and configuration class resolution.

Risks and test signals: risks include hidden launcher regressions masked by `serviceMain`, wrong remaining-argument handling, and failing to expose the launched service. Signals include state assertions, direct execute return-code assertion, and throwable-to-exit-code validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/TestServiceLauncherInnerMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/ExceptionInExecuteLaunchableService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/ExceptionInExecuteLaunchableService.java

Purpose: fixture launchable service that raises controlled exception types from `execute()` so launcher exception mapping can be tested.

Important APIs/types/functions: extends `AbstractLaunchableService`; constants `ARG_THROW_SLE`, `ARG_THROW_IOE`, `ARG_THROWABLE`, `SLE_TEXT`, `OTHER_EXCEPTION_TEXT`, `EXIT_IN_IOE_TEXT`, `IOE_EXIT_CODE`; enum `ExType`; nested `IOECodedException` implements `ExitCodeProvider`.

Control flow: `bindArgs` chooses an exception mode from CLI args. `execute` throws a generic `Exception`, a `ServiceLaunchException`, an `IOException` with an exit code provider, or an `OutOfMemoryError`.

State and persistence behavior: one in-memory `exceptionType` field. No persistence.

Dependencies and integration points: plugs into `ServiceLauncher` tests to check wrapping and exit-code extraction for checked exceptions, launcher exceptions, exit-code-provider IOExceptions, and serious throwables.

Risks and test signals: this fixture intentionally exercises exceptional paths. It is sensitive to launcher treatment of `Throwable` versus `Exception` and to command-line argument matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/ExceptionInExecuteLaunchableService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInConstructorService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInConstructorService.java

Purpose: fixture service that fails during construction to test launcher reflection failure handling.

Important APIs/types/functions: extends `FailureTestService`, exposes fully qualified `NAME`, and its no-arg constructor calls `super(false, false, false, 0)` before throwing `NullPointerException("oops")`.

Control flow: reflective construction immediately throws, before service init/start can occur. Launcher tests expect this to become a service creation failure rather than a lifecycle failure.

State and persistence behavior: no durable state and no usable service state because construction never completes.

Dependencies and integration points: used by `TestServiceLauncherCreationFailures` to validate constructor exception handling in `ServiceLauncher`.

Risks and test signals: confirms constructor exceptions are caught and classified consistently. The fixture is intentionally minimal, so the signal is limited to reflective instantiation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInConstructorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInInitService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInInitService.java

Purpose: fixture service that fails in init and reports a distinctive exit code.

Important APIs/types/functions: extends `FailureTestService`; constants `NAME` and `EXIT_CODE = -1`; constructor configures `failOnInit=true`; overrides package-private `getExitCode`.

Control flow: launcher creates the service successfully, then `BreakableService` init fails. `FailureTestService.createFailureException` converts the lifecycle failure into `ServiceLaunchException(EXIT_CODE, toString())`.

State and persistence behavior: service state moves into failure/stop handling in memory; no persistent state.

Dependencies and integration points: used by launcher creation-failure tests to distinguish init failure from constructor failure.

Risks and test signals: ensures lifecycle exceptions carry service-specific exit codes. The signal depends on `BreakableService` invoking `createFailureException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInInitService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInStartService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInStartService.java

Purpose: fixture service that fails during start and reports a distinctive exit code.

Important APIs/types/functions: extends `FailureTestService`; constants `NAME` and `EXIT_CODE = -2`; constructor configures `failOnStart=true`; overrides `getExitCode`.

Control flow: launcher construction and init succeed; start raises a `ServiceLaunchException` produced by the base fixture's failure factory. Tests assert the launcher surfaces `-2`.

State and persistence behavior: all state is lifecycle failure state on the service instance. No persistence.

Dependencies and integration points: used by `TestServiceLauncherCreationFailures` for start-failure classification.

Risks and test signals: protects launcher rollback/start failure mapping. Narrow fixture but high signal for lifecycle phase attribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInStartService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailingStopInStartService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailingStopInStartService.java

Purpose: fixture service that stops itself during start while its stop operation is configured to fail.

Important APIs/types/functions: extends `FailureTestService`; constants `NAME` and `EXIT_CODE = -4`; constructor sets `failOnStop=true`; `serviceStart` calls `super.serviceStart()` and then `stop()` inside a swallowed catch; overrides `getExitCode`.

Control flow: start completes enough to invoke stop. Stop failure is intentionally caught inside the fixture, allowing launcher tests to check that this edge path can still be treated as a successful run in some launcher scenarios and as recorded failure in direct service tests.

State and persistence behavior: service state and failure cause are in-memory. No persistence.

Dependencies and integration points: integrates with `BreakableService` failure injection and launcher stop-in-start behavior tests.

Risks and test signals: covers a subtle case where stop failure during startup could either abort startup or be ignored. Test signals include stopped-state and failure-cause assertions in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailingStopInStartService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailureTestService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailureTestService.java

Purpose: base fixture for launcher lifecycle failure tests.

Important APIs/types/functions: extends `BreakableService`; constructor parameters `failOnInit`, `failOnStart`, `failOnStop`, and `delay`; overrides `serviceStop`; overrides `createFailureException`; package-private `getExitCode`.

Control flow: inherits failure injection from `BreakableService`. `serviceStop` optionally sleeps before delegating, enabling interrupt timeout tests. `createFailureException` wraps lifecycle failures as `ServiceLaunchException(getExitCode(), toString())`.

State and persistence behavior: stores a final in-memory stop delay and uses `BreakableService` in-memory lifecycle/failure counters. No durable state.

Dependencies and integration points: used by specialized fail-in-constructor/init/start/stop fixtures and interrupt escalation tests.

Risks and test signals: centralizes exit-code behavior for launcher fixtures; changing it affects many launcher tests. Delay-based stop behavior is timing-sensitive but useful for forced shutdown timeout coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailureTestService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/InitInConstructorLaunchableService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/InitInConstructorLaunchableService.java

Purpose: fixture launchable service proving the launcher handles services already initialized by their constructor.

Important APIs/types/functions: extends `AbstractLaunchableService`; constant `NAME`; field `originalConf`; constructor calls `init(originalConf)`; overrides `init`, `bindArgs`, and `execute` with JUnit assertions.

Control flow: construction initializes the service. Later launcher binding sees state `INITED` and returns `null`, meaning no replacement configuration. `execute` asserts the service is `STARTED` and still holds the original constructor configuration.

State and persistence behavior: preserves one in-memory `Configuration` instance as identity-sensitive state. No files.

Dependencies and integration points: used by `TestServiceLauncher` to check no double-init and correct config retention when `bindArgs` returns null after constructor init.

Risks and test signals: catches launcher code that assumes all services start as `NOTINITED` or overwrites config unexpectedly. Assertions inside fixture make failures immediate and phase-specific.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/InitInConstructorLaunchableService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/LaunchableRunningService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/LaunchableRunningService.java

Purpose: primary launchable service fixture that separates lifecycle start from executable work and supports argument/config-driven failure.

Important APIs/types/functions: extends `RunningService` and implements `LaunchableService`; constants `ARG_FAILING` and `EXIT_CODE_PROP`; methods `bindArgs`, `serviceInit`, no-op `serviceStart`, `execute`, `getExitCode`, and `setExitCode`.

Control flow: `bindArgs` asserts state `NOTINITED`, logs args, clones the incoming config, and if `--failing` is present sets `failInRun` and an exit-code property. `serviceInit` reads config-driven failure and exit code. `execute` sleeps for `delayTime`, then returns the configured failure code or zero.

State and persistence behavior: in-memory fields `failInRun`, inherited `delayTime`, and local `exitCode`; configuration values can override them. No durable writes.

Dependencies and integration points: used by launcher and config tests for `LaunchableService.bindArgs`, config propagation, execute return-code handling, and direct access to launched service.

Risks and test signals: guards argument/config precedence and phase ordering. Assertions in `bindArgs` catch premature init; execute return codes drive launcher outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/LaunchableRunningService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/NoArgsAllowedService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/NoArgsAllowedService.java

Purpose: fixture launchable service that rejects any non-configuration command arguments.

Important APIs/types/functions: extends `AbstractLaunchableService`; constant `NAME`; overrides `bindArgs`; throws `ServiceLaunchException(EXIT_COMMAND_ARGUMENT_ERROR, ...)` when remaining args are non-empty.

Control flow: `bindArgs` first delegates to the superclass, then formats every remaining argument and fails if any remain. Launcher command option extraction should strip `--conf` arguments before this point.

State and persistence behavior: no extra state; relies on passed argument list and configuration. No persistence.

Dependencies and integration points: used by launcher tests for successful zero-arg launch, argument-count failure, and config-argument stripping.

Risks and test signals: catches regressions where launcher passes internal command options through to services or fails to report bad user args with the command-argument exit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/NoArgsAllowedService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/NullBindLaunchableService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/NullBindLaunchableService.java

Purpose: launchable fixture verifying that a `bindArgs` implementation may return `null` without breaking launcher initialization.

Important APIs/types/functions: extends `LaunchableRunningService`; constructors; constant `NAME`; overrides `bindArgs(Configuration, List<String>)` to return null.

Control flow: launcher calls `bindArgs`, receives null, and must continue using the existing configuration rather than dereferencing null or discarding config state.

State and persistence behavior: no additional state beyond inherited service fields. No persistence.

Dependencies and integration points: used by `TestServiceLauncher.testNullBindService` as a successful run path.

Risks and test signals: guards launcher null-handling around optional configuration replacement from `LaunchableService.bindArgs`. Signal is simple success: service runs without argument binding replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/NullBindLaunchableService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/RunningService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/RunningService.java

Purpose: simple asynchronous service fixture for launcher tests of non-launchable services that run in a background thread and stop themselves.

Important APIs/types/functions: extends `AbstractService` and implements `Runnable`; constants `NAME`, `DELAY`, `DELAY_TIME`, `FAIL_IN_RUN`, and `FAILURE_MESSAGE`; methods `serviceInit`, `serviceStart`, `run`, and `isInterrupted`.

Control flow: `serviceInit` reads delay and failure flags from configuration. `serviceStart` starts a `SubjectInheritingThread` named after the service. `run` sleeps, optionally records a failure via `noteFailure`, catches interruption, and stops the service.

State and persistence behavior: in-memory fields `delayTime`, `failInRun`, and `interrupted`; configuration seeds runtime behavior. No persistence.

Dependencies and integration points: used by launcher tests for simple service execution, config propagation, failure recording, and wait-for-stop behavior.

Risks and test signals: asynchronous timing can be flaky if delays are too short or threads leak. It provides strong signal for launcher wait behavior and service self-stop handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/RunningService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/StoppingInStartLaunchableService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/StoppingInStartLaunchableService.java

Purpose: fixture launchable service that stops itself during `serviceStart` and must not have `execute()` invoked afterward.

Important APIs/types/functions: extends `AbstractLaunchableService`; constant `NAME`; constructor takes `String name`; overrides `serviceStart` and `execute`.

Control flow: `serviceStart` delegates to the superclass, then immediately calls `stop`. If launcher logic respects stopped state, it returns success without invoking `execute`. If `execute` is called, it throws `ServiceLaunchException(EXIT_SERVICE_LIFECYCLE_EXCEPTION, ...)`.

State and persistence behavior: only service lifecycle state. No persistent state.

Dependencies and integration points: used by `TestServiceLauncher.testStoppingInStartLaunchableService` to check launcher's post-start execute gate.

Risks and test signals: prevents executing a launchable service after it has already transitioned to stopped during startup. Signal is successful launch; any execute call becomes a clear failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/StoppingInStartLaunchableService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/StringConstructorOnlyService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/StringConstructorOnlyService.java

Purpose: fixture proving the launcher can instantiate services that expose only a `String` constructor, a common YARN service pattern.

Important APIs/types/functions: extends `AbstractLaunchableService`; constructor `StringConstructorOnlyService(String name)`; constant fully qualified `NAME`.

Control flow: there is no no-arg constructor. Launcher reflection must fall back to the string-name constructor and then run the inherited launchable service lifecycle.

State and persistence behavior: no additional state beyond base service name and lifecycle fields. No persistence.

Dependencies and integration points: used by `TestServiceLauncher.testServiceLaunchStringConstructor` to validate constructor selection.

Risks and test signals: catches reflection logic that requires no-arg constructors only. Signal is successful service launch via fully qualified class name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/StringConstructorOnlyService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/AbstractHadoopTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/AbstractHadoopTestBase.java

Purpose: JUnit 5 base class that applies a default timeout and names test threads without extending assertion classes.

Important APIs/types/functions: `@Timeout`, `PROPERTY_TEST_DEFAULT_TIMEOUT`, `TEST_DEFAULT_TIMEOUT_VALUE`, static `retrieveTestTimeout`, `@RegisterExtension TestName`, `getMethodName`, `nameTestThread`, and `nameThreadToMethod`.

Control flow: class-level timeout uses the default value constant. `retrieveTestTimeout` parses system property `test.default.timeout`, falling back to 100000 ms on absence or parse failure. Before all tests, the thread is named `JUnit`; before each method, it becomes `JUnit-<method>`.

State and persistence behavior: uses system properties for timeout configuration and in-memory thread names. No persistence.

Dependencies and integration points: integrates with Hadoop's `TestName` extension and JUnit 5 lifecycle. Intended for tests that prefer AssertJ or custom assertion bases.

Risks and test signals: naming improves diagnostics in thread dumps and logs. Risk is duplicated timeout constants with `HadoopTestBase`; parse fallback is explicit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/AbstractHadoopTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/AssertExtensions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/AssertExtensions.java

Purpose: small AssertJ helper for lazy failure descriptions.

Important APIs/types/functions: final `AssertExtensions`, static `dynamicDescription(Callable<String>)`, nested `DynamicDescription extends Description`, and logger-backed error handling.

Control flow: `dynamicDescription` wraps a callable. AssertJ invokes `Description.value()` only when needed; the wrapper calls the callable and returns its result. If evaluation fails, it logs a warning/debug detail and returns null so AssertJ can skip the description.

State and persistence behavior: stores a callable reference in memory. No persistent state.

Dependencies and integration points: deliberately isolated from `LambdaTestUtils` so AssertJ is only required where this class is used. Integrates with AssertJ `describedAs`.

Risks and test signals: protects expensive diagnostic rendering from running on passing assertions and prevents diagnostic failures from hiding the original assertion. Risk is silent null descriptions if the callable fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/AssertExtensions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/CoreTestDriver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/CoreTestDriver.java

Purpose: command-line driver registering selected core Hadoop tests with `ProgramDriver`.

Important APIs/types/functions: `ProgramDriver`, constructors, `run(String[])`, and `main`. Registered programs are `testsetfile`, `testarrayfile`, `testrpc`, and `testipc`.

Control flow: constructor creates or accepts a `ProgramDriver`, registers test classes and descriptions, and prints any registration throwable. `run` calls `pgd.run(argv)`, catches throwable, then exits the JVM with the resulting exit code. `main` constructs and runs the driver.

State and persistence behavior: stores one in-memory `ProgramDriver`. No file persistence, but it calls `System.exit`.

Dependencies and integration points: integrates with old Hadoop command-driver patterns and specific core test classes in `io` and `ipc`.

Risks and test signals: useful for manual/legacy test invocation but risky in embedded tests because it exits the JVM. Error handling prints stack traces rather than using structured logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/CoreTestDriver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/GenericTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/GenericTestUtils.java

Purpose: broad shared test utility class for logging, temp paths, exception assertions, waiting, system-error/log capture, Mockito answers, thread leak checks, file diffs, formatted failures, parallel test sizing, and synthetic filesystem trees.

Important APIs/types/functions: log controls `disableLog/setLogLevel/toLevel`, temp helpers `getTestDir/getTempPath`, `assertExceptionContains`, `waitFor`, `SystemErrCapturer`, `LogCapturer`, `DelayAnswer`, `DelegateAnswer`, `SleepAnswer`, regex asserts, thread checks, `assumeInNativeProfile`, `getFilesDiff`, `failf/failif`, `getTestsThreadCount`, `createFiles/createDirsAndFiles`, `buildPaths`, and private async `put`.

Control flow: most helpers are stateless static utilities. `waitFor` polls a supplier until true or timeout and emits thread diagnostics. Capture classes install appenders or replace `System.err` temporarily. Mockito answers block, delegate, or sleep around method calls. File-tree helpers generate paths recursively, then create directories and files asynchronously using a shared blocking thread pool.

State and persistence behavior: static atomic sequence and static executor are process state. Temp/file helpers write under `test.build.data` or `target/test/data`; filesystem tree creation writes through a Hadoop `FileSystem`.

Dependencies and integration points: integrates JUnit assertions/assumptions, Mockito, log4j/SLF4J, Hadoop FS utilities, `DurationInfo`, thread diagnostics, and Hadoop functional future helpers.

Risks and test signals: broad shared surface means regressions affect many tests. Risks include global logging mutation, thread-pool resource use, capture cleanup requirements, and timeout flakiness. Strong utility signals include detailed timeout diagnostics, exact exception text validation, leak checks, and deterministic path naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/GenericTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/HadoopTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/HadoopTestBase.java

Purpose: assertion-enabled Hadoop JUnit 5 base class that applies a default timeout and test-thread naming.

Important APIs/types/functions: extends `Assertions`; class-level `@Timeout`; constants `PROPERTY_TEST_DEFAULT_TIMEOUT` and `TEST_DEFAULT_TIMEOUT_VALUE`; instance `retrieveTestTimeout`; `@RegisterExtension TestName`; `getMethodName`; lifecycle hooks `nameTestThread` and `nameThreadToMethod`.

Control flow: timeout uses 100000 ms by default. `retrieveTestTimeout` reads system property `test.default.timeout` and falls back on parse errors. JUnit lifecycle methods rename the current thread to `JUnit` and then `JUnit-<method>`.

State and persistence behavior: only in-memory timeout field and thread name; reads JVM system property. No durable state.

Dependencies and integration points: common base for Hadoop tests wanting inherited JUnit assertions, unlike `AbstractHadoopTestBase`.

Risks and test signals: helps diagnose hung tests and gives consistent timeouts. The `defaultTimeout` field is stored but not otherwise used beyond construction-era retrieval, so class-level annotation is the real enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/HadoopTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/LambdaTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/LambdaTestUtils.java

Purpose: Java-8-friendly test utilities for lambda-based retries, eventual assertions, exception interception, optional assertions, checked-exception wrapping, UGI `doAs`, future exception unwrapping, and retry policies.

Important APIs/types/functions: `await`, `eventually`, many overloads of `intercept`, `interceptAndValidateMessageContains`, `assertOptionalEquals`, `assertOptionalUnset`, `eval`, `notNull`, `doAs`, `interceptFuture`, `verifyCause`, `TimeoutHandler`, `GenerateTimeout`, `FixedRetryInterval`, `ProportionalRetryInterval`, `FailFastException`, `VoidCallable`, `VoidCaller`, `PrivilegedOperation`, and `PrivilegedVoidOperation`.

Control flow: `await` repeatedly evaluates a boolean callable with pluggable retry and timeout exception generation. `eventually` retries a value/void closure until it succeeds or timeout expires. Intercept helpers execute callables and return expected exceptions, rethrowing wrong types and validating text. Future helpers unwrap `ExecutionException` causes before applying intercept logic.

State and persistence behavior: retry policy classes keep invocation/current interval counters in memory. No persistent state.

Dependencies and integration points: integrates JUnit assertions, `GenericTestUtils.assertExceptionContains`, Hadoop `Preconditions`, `Time`, and `UserGroupInformation.doAs`.

Risks and test signals: central to async/flaky-condition tests. Risks include masking non-retryable errors if callers do not use `FailFastException`; code explicitly rethrows interruption, virtual machine errors, and fail-fast exceptions. Signals include robust assertion messages and nested-future cause validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/LambdaTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MetricsAsserts.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MetricsAsserts.java

Purpose: Mockito-based helpers for Hadoop metrics source tests.

Important APIs/types/functions: `mockMetricsSystem`, `mockMetricsRecordBuilder`, `getMetrics`, matchers `eqName` and `anyInfo`, gauge/counter/tag getters and assertions for int/long/double/float/string, greater-than assertions, `assertQuantileGauges`, and `assertInverseQuantileGauges`.

Control flow: `mockMetricsSystem` installs a mocked `MetricsSystem` into `DefaultMetricsSystem`. `mockMetricsRecordBuilder` creates a builder mock that logs method calls and returns itself for fluent methods or its parent collector. `getMetrics` invokes a source against the mock collector. Getter methods capture values using `ArgumentCaptor` and assert exactly one captured metric where appropriate.

State and persistence behavior: mutates global `DefaultMetricsSystem` instance when mocking. Captured metric state is Mockito in-memory state. No durable state.

Dependencies and integration points: integrates Hadoop metrics2 APIs, mutable quantiles, Interns `info`, Mockito matchers/captors, and JUnit assertions.

Risks and test signals: global metrics-system replacement can leak if tests do not isolate it. Signals are strong for exact metric names because matchers compare `MetricsInfo.name()` and require one captured value for most getters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MetricsAsserts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MockitoUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MockitoUtil.java

Purpose: Hadoop-specific Mockito conveniences for IPC protocol mocks and conditional stack-sensitive failures.

Important APIs/types/functions: `mockProtocol(Class<T>)`, `doThrowWhenCallStackMatches(Throwable, String)`, and `verifyZeroInteractions(Object...)`.

Control flow: `mockProtocol` creates a Mockito mock with `Closeable` as an extra interface because Hadoop IPC proxies often require both protocol and close behavior. `doThrowWhenCallStackMatches` installs an answer that sets the throwable stack trace to the current stack, checks each element against a regex, throws if matched, otherwise calls the real method. `verifyZeroInteractions` delegates to `verifyNoInteractions`.

State and persistence behavior: no persistence; state is Mockito stubbing and throwable stack trace mutation.

Dependencies and integration points: integrates with Mockito and Hadoop IPC test patterns.

Risks and test signals: stack-regex behavior is brittle across refactors but useful for targeted failure injection. Mock protocol extra interfaces prevent close-cast failures in tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MockitoUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MoreAsserts.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MoreAsserts.java

Purpose: small assertion helper class for collection equality, CompletableFuture completion state, and AssertJ equality messages.

Important APIs/types/functions: overloaded `assertEquals` for arrays/iterables and iterable/iterable, `assertFutureCompletedSuccessfully`, `assertFutureFailedExceptionally`, and `assertEqual`.

Control flow: iterable assertions compare element-by-element and then assert neither side has extra elements. Future assertions inspect `isDone` and `isCompletedExceptionally`. `assertEqual` delegates to AssertJ with a formatted description.

State and persistence behavior: no state; pure assertion utilities.

Dependencies and integration points: combines JUnit assertions and AssertJ. Intended as supplementary helpers where standard assertions are verbose.

Risks and test signals: collection assertions report index-specific mismatches but use terse extra-element messages. Future assertions check state only; they do not retrieve results or inspect failure causes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MoreAsserts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MultithreadedTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MultithreadedTestUtil.java

Purpose: utility framework for stress-testing threaded or synchronized code with coordinated test threads and deferred exception propagation.

Important APIs/types/functions: `TestContext`, `TestingThread`, and `RepeatingTestThread`, plus methods `addThread`, `startThreads`, `waitFor`, `stop`, `threadFailed`, `threadDone`, `shouldRun`, `doWork`, and `doAnAction`.

Control flow: tests create a `TestContext`, add `TestingThread` instances, start all threads, and wait or stop. Each `TestingThread` runs `doWork` inside `work`, reports thrown errors to the context, and signals completion. Repeating threads loop `doAnAction` while the context should run and the thread is not stopped.

State and persistence behavior: context maintains in-memory stopped flag, first error, all threads, and finished threads. No persistence.

Dependencies and integration points: threads extend `SubjectInheritingThread`, preserving Hadoop subject/security context. Uses Hadoop `Time` for deadlines and SLF4J logging.

Risks and test signals: errors are deferred to the coordinator, so failing worker threads become test failures. Risks include tests that forget to stop repeating threads or rely on coarse timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MultithreadedTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/PlatformAssumptions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/PlatformAssumptions.java

Purpose: JUnit assumption helpers for OS-specific tests.

Important APIs/types/functions: constants `OS_NAME` and `WINDOWS`; static methods `assumeNotWindows()`, `assumeNotWindows(String)`, and `assumeWindows()`.

Control flow: methods inspect `System.getProperty("os.name")`. If the platform does not match the requested assumption, they throw `TestAbortedException`, causing the JUnit test to be skipped/aborted rather than failed.

State and persistence behavior: `OS_NAME` and `WINDOWS` are static process-time values. No persistence.

Dependencies and integration points: integrates with JUnit 5/OpenTest4J's `TestAbortedException`. Used by tests that have Unix-only or Windows-only behavior.

Risks and test signals: simple `startsWith("Windows")` detection is stable for common JVMs but not a full platform abstraction. Test signal is skip behavior rather than assertion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/PlatformAssumptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/ReflectionUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/ReflectionUtils.java

Purpose: test-only reflection helpers for reading static primitive/string field values and modifying final fields.

Important APIs/types/functions: `getStringValueOfField(Field)`, `setFinalField(Class<T>, T, String, Object)`, and `getModifiersField()`.

Control flow: `getStringValueOfField` switches on field type names and returns a string for supported primitive/string static fields. `setFinalField` looks up a declared field, makes it accessible, clears the `FINAL` modifier via the private `Field.modifiers` field, and sets the new value. `getModifiersField` reflectively calls `Class.getDeclaredFields0` to locate `modifiers`.

State and persistence behavior: mutates in-memory object/class fields; no persistence.

Dependencies and integration points: integrates with JDK reflection internals and is intended for tests that need to inspect or override otherwise inaccessible state.

Risks and test signals: highly JDK-version-sensitive because it accesses private reflection internals and may require module opens. Null return for unsupported field types is a deliberate limited-scope behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/ReflectionUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/StatUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/StatUtils.java

Purpose: test helper for querying and changing filesystem permissions by shelling out to platform-specific commands.

Important APIs/types/functions: nested `Permission` value class, `getPermissionFromProcess`, `setPermissionFromProcess`, `removeDomain`, and `getPermissionStringFromProcess`.

Control flow: query builds `Shell.getGetPermissionCommand`, appends target path, starts a process, reads the first stdout line, tokenizes symbolic permissions, link count, owner, and group, strips Windows domains, and returns `FsPermission`. Set builds `Shell.getSetPermissionCommand` and executes it similarly.

State and persistence behavior: `setPermissionFromProcess` mutates real filesystem permissions. Query has no durable state beyond process execution.

Dependencies and integration points: integrates Hadoop `Shell`, `FsPermission`, Java `ProcessBuilder`, and a single-thread executor for stdout reading.

Risks and test signals: process handling is platform-sensitive and reads only first stdout line. The code starts an executor then calls `awaitTermination` before submitting, which is unusual but harmless for simple commands. Tests using it depend on shell command availability and permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/StatUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestGenericTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestGenericTestUtils.java

Purpose: self-tests key behaviors of `GenericTestUtils`.

Important APIs/types/functions: extends `GenericTestUtils`; tests `assertExceptionContains`, `LogCapturer`, `waitFor`, and `toLevel`; nested `BrokenException` returns null from `toString`.

Control flow: exception tests verify null throwable, null `toString`, wrong text with nested cause, and successful text matching. Log tests capture SLF4J output, assert contents, clear buffer, stop capture, and verify no further output. Wait tests validate null supplier and invalid timing arguments. Level tests verify valid and invalid string conversion with default fallback.

State and persistence behavior: uses in-memory log capture buffers and no durable state.

Dependencies and integration points: validates the utility class used widely across Hadoop tests, with JUnit timeouts on log capture paths.

Risks and test signals: protects error-message constants and capture cleanup behavior. Narrow coverage leaves many `GenericTestUtils` helpers untested here, but the covered areas are high reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestGenericTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestJUnitSetup.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestJUnitSetup.java

Purpose: verifies the test JVM has Java assertions enabled.

Important APIs/types/functions: single JUnit test `testJavaAssert`, SLF4J logger, and Java `assert` statement.

Control flow: the test executes `assert false : "Good! Java assert is on."`. If assertions are enabled, an `AssertionError` is caught and logged, and the test passes. If assertions are disabled, execution reaches `fail("Java assert does not work.")`.

State and persistence behavior: no state beyond JVM assertion configuration and log output. No persistence.

Dependencies and integration points: provides a build/test environment sanity check for Hadoop tests that rely on Java assertions.

Risks and test signals: failure indicates the test runner did not enable `-ea`. The check is intentionally direct and environment-dependent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestJUnitSetup.java -->
