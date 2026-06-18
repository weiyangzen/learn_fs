# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/ExitTrackingServiceLauncher.java

Purpose: test subclass of `ServiceLauncher` that records the exit exception while still delegating to the normal exit path.

Important APIs/types/functions: generic `ExitTrackingServiceLauncher<S extends Service>`, overridden `exit(ExitUtil.ExitException)`, overridden `exit(int, String)`, public `bindCommandOptions`, and `getExitException`.

Control flow: tests instantiate the launcher with a service class name, then normal launcher code eventually calls `exit`. This subclass stores the exception in `exitException` before delegating to `super.exit`, and wraps integer/message exits as `ServiceLaunchException`.

State and persistence behavior: one in-memory `ExitException` field records the last exit. There is no filesystem state.

Dependencies and integration points: depends on the test base disabling system exits. It exposes protected command option binding so command extraction can be tested directly.

Risks and test signals: useful for tests that need to assert exit details without losing normal launcher behavior. Risk is that calling `super.exit` still raises if `ExitUtil` is not disabled, so it is tied to the base class setup.
