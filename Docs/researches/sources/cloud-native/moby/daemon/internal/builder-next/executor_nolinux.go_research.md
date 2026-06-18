<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_nolinux.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor_nolinux.go

Purpose: provides non-Linux graphdriver executor stubs for BuildKit.

Important APIs and control flow: `stubExecutor.Run` and `Exec` return errors stating the BuildKit executor is not implemented for the current `runtime.GOOS`. `newExecutorGD` returns the stub executor with no proxy provider.

State and persistence: no state is read or written.

Dependencies and integration: selected by `!linux` builds to satisfy graphdriver controller construction paths where native executor support is unavailable.

Risks: any non-Linux graphdriver BuildKit execution path will fail at runtime with the stub error. Containerd snapshotter mode has separate controller behavior and may not use this stub.

Test signals: compile coverage on non-Linux platforms; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_nolinux.go -->
