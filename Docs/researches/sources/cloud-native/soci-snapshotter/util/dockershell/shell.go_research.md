# sources/cloud-native/soci-snapshotter/util/dockershell/shell.go

Purpose: this file provides a chainable shell-like interface for executing commands inside a Docker container via `dockershell/exec`.

Important APIs and types: `Supported` delegates Docker support check. `Reporter` abstracts error/log/stdout/stderr sinks. `DefaultReporter` writes to stdout/stderr. `Shell` embeds `*dexec.Exec`, tracks the last error and an invalid flag. Core methods include `Fatal`, `Err`, `IsInvalid`, `Refresh`, `X`, `XLog`, `Gox`, `Pipe`, `Retry`, `O`, `OLog`, `CombinedOLog`, `R`, and `ForEach`. `C` is a command slice helper for `Pipe`.

Control flow: most methods no-op if the shell is invalid. `X`, `O`, `Pipe`, and exhausted `Retry` mark the shell invalid on failure. `XLog`, `OLog`, `CombinedOLog`, and `Gox` log errors but allow later commands. `Pipe` starts each command with the previous command's stdout as stdin, then waits in reverse order to avoid truncating stdout pipes. `R` returns pipe readers and runs the command in a goroutine, closing pipes with errors on failure. `ForEach` streams stdout lines to a callback and stderr to the reporter.

State and persistence: shell invalid/error state is in memory, protected by a mutex for the invalid flag. Commands can mutate container state but the shell has no persistent storage.

Dependencies and integration points: integrates the Docker exec wrapper and is used by integration tests for command orchestration inside containers.

Risks: `Gox` launches background goroutines without cancellation or wait handles, so callers cannot reliably synchronize. `ForEach` does not return scanner errors. `Retry` logs attempts starting at `0/num`, which is mildly misleading. Reporter comments contain copy-paste wording mistakes but behavior is clear.

Test signals: no direct tests in this subset. The most important behaviors to integration-test are invalid-state short-circuiting, pipe lifecycle, and background command handling.
