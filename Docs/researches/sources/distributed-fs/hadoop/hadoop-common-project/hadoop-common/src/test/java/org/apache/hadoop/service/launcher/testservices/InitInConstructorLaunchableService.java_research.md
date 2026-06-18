# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/InitInConstructorLaunchableService.java

Purpose: fixture launchable service proving the launcher handles services already initialized by their constructor.

Important APIs/types/functions: extends `AbstractLaunchableService`; constant `NAME`; field `originalConf`; constructor calls `init(originalConf)`; overrides `init`, `bindArgs`, and `execute` with JUnit assertions.

Control flow: construction initializes the service. Later launcher binding sees state `INITED` and returns `null`, meaning no replacement configuration. `execute` asserts the service is `STARTED` and still holds the original constructor configuration.

State and persistence behavior: preserves one in-memory `Configuration` instance as identity-sensitive state. No files.

Dependencies and integration points: used by `TestServiceLauncher` to check no double-init and correct config retention when `bindArgs` returns null after constructor init.

Risks and test signals: catches launcher code that assumes all services start as `NOTINITED` or overwrites config unexpectedly. Assertions inside fixture make failures immediate and phase-specific.
