# sources/control-plane/rook/tests/framework/utils/exec_utils.go

Purpose: this file implements a generic OS command runner with stdin support and captured stdout/stderr for test utilities.

Important APIs/types/functions: `CommandArgs` describes command, args, stdin payload, and environment variables. `CommandOut` carries stdout, stderr, exit code, and error. `ExecuteCommand` runs the command and streams/captures output.

Control flow: `ExecuteCommand` builds `exec.Command`, appends caller-provided environment entries, obtains stdout/stdin/stderr pipes, starts goroutines scanning stdout/stderr, starts the process, optionally writes stdin, waits, and returns captured buffers plus exit status when available.

State and persistence behavior: no local persistence. It may execute commands with arbitrary external side effects, especially kubectl/oc calls from helpers.

Dependencies and integration points: used by `K8sHelper.KubectlWithStdin`. Depends on Go `os/exec`, `bufio.Scanner`, capnslog, and Rook `utilexec.ExitStatus`.

Risks: `cmd.Env = append(cmd.Env, ...)` starts from nil, so only supplied env vars are passed, not the parent environment; callers here usually supply none. Scanner default token limits may truncate very long output lines. Goroutine scanner errors are ignored. If no stdin is written, the stdin pipe is not explicitly closed before wait.

Test signals: command success/failure, stdin application, stderr filtering for “no buildable Go source files”, and correct exit code extraction are relevant.
