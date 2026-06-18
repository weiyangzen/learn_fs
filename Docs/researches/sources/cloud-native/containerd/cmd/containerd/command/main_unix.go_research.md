# sources/cloud-native/containerd/cmd/containerd/command/main_unix.go

Purpose: provides Unix-like daemon signal handling for Linux, Darwin, FreeBSD, and Solaris builds.

Important APIs/functions: `handledSignals` includes `SIGTERM`, `SIGINT`, `SIGUSR1`, and `SIGPIPE`; `handleSignals()` starts a goroutine and returns a `done` channel consumed by daemon startup.

Control flow: the goroutine waits for either the initialized `*server.Server` from `serverC` or an OS signal. `SIGPIPE` is ignored to avoid noisy nested logging. `SIGUSR1` triggers `dumpStacks(true)`. Other handled signals notify stopping, cancel the root context, stop the server if available, close `done`, and exit.

State and persistence: stores only an in-goroutine pointer to the server. `SIGUSR1` stack dumps persist to a temp file through `dumpStacks(true)`.

Dependencies/integration: called by daemon startup after `signal.Notify(signals, handledSignals...)`. Integrates with systemd notification variants via `notifyStopping()` and with `server.Stop()`.

Risks: if multiple termination signals arrive, `done` closes once because the goroutine returns. Shutdown before `serverC` delivery cancels context without stopping a nil server. The buffered signal channel in `main.go` reduces but does not remove all ordering risks.

Test signals: no local unit tests. Behavior is platform/runtime integration oriented.
