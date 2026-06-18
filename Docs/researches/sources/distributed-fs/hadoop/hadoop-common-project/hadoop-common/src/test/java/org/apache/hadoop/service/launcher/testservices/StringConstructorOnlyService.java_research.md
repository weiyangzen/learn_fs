# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/StringConstructorOnlyService.java

Purpose: fixture proving the launcher can instantiate services that expose only a `String` constructor, a common YARN service pattern.

Important APIs/types/functions: extends `AbstractLaunchableService`; constructor `StringConstructorOnlyService(String name)`; constant fully qualified `NAME`.

Control flow: there is no no-arg constructor. Launcher reflection must fall back to the string-name constructor and then run the inherited launchable service lifecycle.

State and persistence behavior: no additional state beyond base service name and lifecycle fields. No persistence.

Dependencies and integration points: used by `TestServiceLauncher.testServiceLaunchStringConstructor` to validate constructor selection.

Risks and test signals: catches reflection logic that requires no-arg constructors only. Signal is successful service launch via fully qualified class name.
