# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/AbstractServiceLauncherTestBase.java

Purpose: shared base for service launcher tests. It disables real JVM exits, provides launch/assert helpers, creates temporary XML configs, and stops launched services after each test.

Important APIs/types/functions: `LauncherExitCodes`, `ExitUtil.disableSystemExit/disableSystemHalt`, `ServiceLauncher.serviceMain`, `ServiceLauncher.launchService`, `ServiceLaunchException`, `ServiceOperations.stopQuietly`, `failf/failif`, `configFile`, `newConf`, `assertLaunchOutcome`, and `launchExpectingException`.

Control flow: `@BeforeAll` converts exits/halts into exceptions; `@BeforeEach` names the test thread; `@AfterEach` quietly stops any service registered via `setServiceToTeardown`. Launch helpers either call the CLI entry point or construct `ServiceLauncher`, then assert exit code and expected exception text.

State and persistence behavior: holds one in-memory teardown service reference. Configuration files are persisted under `target/launcher/conf` for command-line config tests.

Dependencies and integration points: centralizes interaction between JUnit tests and the launcher, ExitUtil, configuration XML writing, and service lifecycle cleanup.

Risks and test signals: incorrect exit disabling would terminate the test JVM. The base reduces that risk and standardizes assertions. Config file creation under `target` is intentional but can leave test artifacts.
