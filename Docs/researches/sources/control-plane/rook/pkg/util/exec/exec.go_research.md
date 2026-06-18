# sources/control-plane/rook/pkg/util/exec/exec.go

## Purpose
`exec.go` implements Rook's local command execution abstraction, output capture, timeout handling, logging, and generic exit-code extraction.

## Important APIs, Types, and Functions
`Executor` defines command execution methods. `CommandExecutor` implements them. Methods include `ExecuteCommand()`, `ExecuteCommandWithEnv()`, `ExecuteCommandWithOutput()`, `ExecuteCommandWithCombinedOutput()`, `ExecuteCommandWithTimeout()`, and `ExecuteCommandWithStdin()`. `IsTimeout()` detects timeout errors. Internal helpers start commands, log stdout/stderr, run output-capturing commands, and append stderr details for output-only failures. `ExtractExitCode()` handles Go exec errors, Kubernetes exec errors, status errors, and some string-form errors.

## Control Flow, State, and Persistence
Commands are executed as OS subprocesses. Timeout execution sends interrupt on the first timeout tick and kill on the next. Output is trimmed. `logOutput()` may adjust capnslog repo logger level to show child process logs. There is no filesystem persistence except whatever commands perform.

## Dependencies and Integration Points
It depends on Go `os/exec`, capnslog, Kubernetes API/status and utils exec errors. It is a shared boundary for Rook's system and Ceph command invocations.

## Risks
Timeout handling uses repeated `time.After(timeout)`, so total kill time can be about twice the timeout. Environment override replaces the process environment instead of appending. `ExtractExitCode()` string parsing is fragile but useful as fallback. Logging command args can expose sensitive values if callers pass secrets.

## Test Signals
`exec_test.go` covers error text extraction, exit-code extraction variants, fake timeout detection, stdin/nil-stdin command execution, command failure, and timeout.
