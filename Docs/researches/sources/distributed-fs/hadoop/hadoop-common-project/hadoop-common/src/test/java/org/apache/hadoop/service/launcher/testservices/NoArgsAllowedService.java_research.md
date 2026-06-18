# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/service/launcher/testservices/NoArgsAllowedService.java

Purpose: fixture launchable service that rejects any non-configuration command arguments.

Important APIs/types/functions: extends `AbstractLaunchableService`; constant `NAME`; overrides `bindArgs`; throws `ServiceLaunchException(EXIT_COMMAND_ARGUMENT_ERROR, ...)` when remaining args are non-empty.

Control flow: `bindArgs` first delegates to the superclass, then formats every remaining argument and fails if any remain. Launcher command option extraction should strip `--conf` arguments before this point.

State and persistence behavior: no extra state; relies on passed argument list and configuration. No persistence.

Dependencies and integration points: used by launcher tests for successful zero-arg launch, argument-count failure, and config-argument stripping.

Risks and test signals: catches regressions where launcher passes internal command options through to services or fails to report bad user args with the command-argument exit code.
