# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_nolinux.go

Purpose: provides non-Linux reexec initialization for buildkitd.

Important behavior: on `!linux` builds, package init calls `reexec.Init()` and exits with status 0 when the process is a reexecuted child command.

State and dependencies: process-control side effect only. Depends on `github.com/moby/sys/reexec` and `os.Exit`.

Risks and test signals: incorrect reexec handling can break helper subprocesses on non-Linux platforms. There are no direct tests in this subset.
