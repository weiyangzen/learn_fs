<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_linux.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_linux.go

Purpose: defines Linux process attributes for starting supervised containerd.

Important APIs and types: `containerdSysProcAttr() *syscall.SysProcAttr`.

Control flow: returns attributes with `Setsid: true` and `Pdeathsig: SIGKILL`.

State and persistence: no persistent state; affects child process/session behavior.

Dependencies and integration: called by `remote_daemon.go` before `exec.Command.Start`.

Risks: `Pdeathsig` is sensitive to Go runtime thread behavior; `remote_daemon.go` locks the OS thread to avoid premature child death.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_linux.go -->
