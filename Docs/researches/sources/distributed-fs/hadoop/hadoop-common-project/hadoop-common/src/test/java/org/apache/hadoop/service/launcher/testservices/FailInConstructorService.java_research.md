# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/FailInConstructorService.java

Purpose: fixture service that fails during construction to test launcher reflection failure handling.

Important APIs/types/functions: extends `FailureTestService`, exposes fully qualified `NAME`, and its no-arg constructor calls `super(false, false, false, 0)` before throwing `NullPointerException("oops")`.

Control flow: reflective construction immediately throws, before service init/start can occur. Launcher tests expect this to become a service creation failure rather than a lifecycle failure.

State and persistence behavior: no durable state and no usable service state because construction never completes.

Dependencies and integration points: used by `TestServiceLauncherCreationFailures` to validate constructor exception handling in `ServiceLauncher`.

Risks and test signals: confirms constructor exceptions are caught and classified consistently. The fixture is intentionally minimal, so the signal is limited to reflective instantiation behavior.
