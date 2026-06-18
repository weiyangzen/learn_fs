## sources/distributed-fs/ipfs-kubo/test/dependencies/go-timeout/main.go

Purpose: portable timeout wrapper used by tests where GNU `timeout` may not be available.

Important APIs and control flow: `main` parses `<timeout-in-sec> <command ...>`, creates `context.WithTimeout`, runs `exec.CommandContext`, wires stdin/stdout/stderr through, waits, and exits with `124` on timeout. For command failures it extracts `syscall.WaitStatus` and forwards the child exit status; unexpected execution or wait-status errors exit `255`.

State and dependencies: no persistent state is written; it depends on Go `context`, `os/exec`, and platform wait status support. Integration point is shell tests that need bounded command execution while preserving child output and exit codes.

Risks: signal termination and non-Unix wait semantics can be platform-sensitive, and `cmd.Start` errors are printed but still followed by `cmd.Wait`, which may produce a secondary error path. Test signal is command timeout returning 124 and normal failures retaining the child code.
