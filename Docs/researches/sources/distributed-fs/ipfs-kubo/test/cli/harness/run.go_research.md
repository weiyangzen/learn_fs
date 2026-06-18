# sources/distributed-fs/ipfs-kubo/test/cli/harness/run.go

Purpose: process execution layer for the CLI harness, with captured output, environment injection, and command customization.

Important APIs/types/functions: `Runner`, `CmdOpt`, `RunFunc`, `RunRequest`, `RunResult`, `ExitCode`, `environToMap`, `Run`, `MustRun`, `AssertNoError`, and command options `RunWithEnv`, `RunWithPath`, `RunWithStdin`, `RunWithStdinStr`, `RunWithStdout`, `RunWithStderr`.

Control flow: `Run` creates `exec.Command`, attaches `Buffer` captures, optionally mirrors output in verbose mode, sets working directory and env, applies options, and calls either `cmd.Run` or a custom function such as `Start`. It returns a `RunResult` with output, error, exit error, and command.

State and persistence: no persistence beyond spawned processes and their outputs. `Runner.Env` and `Dir` define command context.

Dependencies/integration: central for all `Node.IPFS`, daemon startup, and shell/build helpers.

Risks: `strings.Split` without `SplitN` can truncate env values containing `=`. `RunWithStderr` writes to `cmd.Stdout` instead of `cmd.Stderr`, likely a bug in stderr mirroring. `ExitCode` requires a populated process state and is unsafe for running started commands. Test signals are process exit status and captured stdout/stderr.
