<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/util/util.go -->
# sources/control-plane/csi-driver-smb/pkg/util/util.go

Purpose: Provides small shared utilities for timed execution, bounded PowerShell command execution on Windows, and case-insensitive map updates.

Important APIs/types/functions: `MaxPathLengthWindows` is a Windows path constant. `powershellCmdSem` limits concurrent PowerShell commands to three. `ExecFunc` and `TimeoutFunc` define callback signatures. `WaitUntilTimeout` runs `execFunc` in a goroutine and returns either its error or `timeoutFunc` after a duration. `RunPowershellCmd` executes `powershell -Mta -NoProfile -Command` with optional environment additions under the semaphore. `SetKeyValueInMap` inserts or overwrites a key case-insensitively.

Control flow: `WaitUntilTimeout` uses a buffered done channel to avoid blocking the goroutine when the timeout branch wins, but it does not cancel the underlying `execFunc`. `RunPowershellCmd` acquires semaphore capacity before command creation and releases it with defer.

State and persistence behavior: Global semaphore is package-level process state. Commands inherit the environment plus provided env strings and can perform arbitrary external side effects.

Dependencies and integration points: `nodeserver.go` uses `WaitUntilTimeout` around SMB mount calls and uses `SetKeyValueInMap` for ephemeral volume context. Windows mounter code can use `RunPowershellCmd` through related packages.

Risks: Timed-out `execFunc` continues running in the background; callers must ensure the operation is safe to outlive the timeout. `RunPowershellCmd` logs command strings at high verbosity and could expose sensitive command text if callers include secrets. The semaphore bounds concurrency but has no context cancellation.

Test signals: `util_test.go` covers success, error, timeout, goroutine leak behavior after waiting, and map update semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/util/util.go -->
