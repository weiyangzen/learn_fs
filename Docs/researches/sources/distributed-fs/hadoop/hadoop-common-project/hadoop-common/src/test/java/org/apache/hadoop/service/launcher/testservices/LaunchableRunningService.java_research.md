# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/LaunchableRunningService.java

Purpose: primary launchable service fixture that separates lifecycle start from executable work and supports argument/config-driven failure.

Important APIs/types/functions: extends `RunningService` and implements `LaunchableService`; constants `ARG_FAILING` and `EXIT_CODE_PROP`; methods `bindArgs`, `serviceInit`, no-op `serviceStart`, `execute`, `getExitCode`, and `setExitCode`.

Control flow: `bindArgs` asserts state `NOTINITED`, logs args, clones the incoming config, and if `--failing` is present sets `failInRun` and an exit-code property. `serviceInit` reads config-driven failure and exit code. `execute` sleeps for `delayTime`, then returns the configured failure code or zero.

State and persistence behavior: in-memory fields `failInRun`, inherited `delayTime`, and local `exitCode`; configuration values can override them. No durable writes.

Dependencies and integration points: used by launcher and config tests for `LaunchableService.bindArgs`, config propagation, execute return-code handling, and direct access to launched service.

Risks and test signals: guards argument/config precedence and phase ordering. Assertions in `bindArgs` catch premature init; execute return codes drive launcher outcomes.
