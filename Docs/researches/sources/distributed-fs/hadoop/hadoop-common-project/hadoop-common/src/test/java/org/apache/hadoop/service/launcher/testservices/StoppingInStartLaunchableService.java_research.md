# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/StoppingInStartLaunchableService.java

Purpose: fixture launchable service that stops itself during `serviceStart` and must not have `execute()` invoked afterward.

Important APIs/types/functions: extends `AbstractLaunchableService`; constant `NAME`; constructor takes `String name`; overrides `serviceStart` and `execute`.

Control flow: `serviceStart` delegates to the superclass, then immediately calls `stop`. If launcher logic respects stopped state, it returns success without invoking `execute`. If `execute` is called, it throws `ServiceLaunchException(EXIT_SERVICE_LIFECYCLE_EXCEPTION, ...)`.

State and persistence behavior: only service lifecycle state. No persistent state.

Dependencies and integration points: used by `TestServiceLauncher.testStoppingInStartLaunchableService` to check launcher's post-start execute gate.

Risks and test signals: prevents executing a launchable service after it has already transitioned to stopped during startup. Signal is successful launch; any execute call becomes a clear failure.
