# sources/distributed-fs/beegfs-go/ctl/cmd/beegfs/main.go

Purpose: entry point for the `beegfs` CTL binary, including panic traceback handling for setuid/setgid packaging scenarios.

Important API is `main`. It imports `net/http/pprof` for side-effect registration and delegates execution to `ctl/internal/cmd.Execute`.

Control flow: if effective UID is root, it resets Go traceback mode to `single` to counter secure-mode suppression from setgid packaging. If effective UID/GID differs from real UID/GID and the process is not root, it installs a deferred recover handler that prints a warning-style panic message noting stack traces may be suppressed. Finally it exits with the command execution status.

State and persistence: it mutates runtime debug traceback state and may write to stderr on recovered panic. It does not persist files.

Dependencies are `os`, `fmt`, `runtime/debug`, pprof side effects, and the root CTL command package.

Integration points are packaged binary permissions, Go runtime secure mode, pprof registration, and cobra command execution.

Risks: recover catches only panics on the main goroutine. Importing pprof registers handlers only if an HTTP server is started elsewhere. The root check changes traceback behavior globally for the process.

Test signals: no direct tests for main; behavior is mostly integration/runtime-environment dependent.
