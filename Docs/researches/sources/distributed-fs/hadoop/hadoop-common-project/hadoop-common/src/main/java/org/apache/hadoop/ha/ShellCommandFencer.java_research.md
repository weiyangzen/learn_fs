# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ShellCommandFencer.java

Purpose: Built-in fencer that executes an operator-provided shell command and treats exit code 0 as successful fencing.

Important APIs and types: `ShellCommandFencer extends Configured implements FenceMethod`. Key methods are `checkArgs()`, `tryFence()`, `parseArgs()`, `abbreviate()`, `setConfAsEnvVars()`, and `addTargetInfoAsEnvVars()`.

Control flow: `checkArgs()` rejects missing command text. `tryFence()` chooses a command based on the target's intended HA state when two comma-separated commands are supplied, starts `bash -e -c` or `cmd.exe /c`, injects Hadoop configuration and target/source variables into the environment, closes stdin, pumps stdout/stderr, waits for completion, and returns `rc == 0`.

State and persistence: No persistent state. It exports potentially large configuration state as environment variables and performs arbitrary external side effects through the configured command.

Dependencies and integration points: Used through `NodeFencer` alias `shell`. Relies on `HAServiceTarget.getFencingParameters()`, `Shell.WINDOWS`, `StreamPumper`, and operator scripts.

Risks: No built-in timeout; hung scripts can hang failover. Commands run via shell, so quoting and injection risks belong to configuration. Environment values can expose sensitive config in child process environments. Two-command parsing simply splits on comma, so commands containing commas are unsupported.

Test signals: `TestShellCommandFencer` covers missing arguments, exit code handling, command abbreviation, environment variable generation, output pumping, and source/target command selection.
