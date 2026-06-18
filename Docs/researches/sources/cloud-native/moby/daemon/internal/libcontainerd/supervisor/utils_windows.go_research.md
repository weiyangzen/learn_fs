<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_windows.go

Purpose: supplies Windows process attributes for supervised containerd startup.

Important APIs and types: `containerdSysProcAttr() *syscall.SysProcAttr`.

Control flow: returns nil; no special process attributes are used on Windows.

State and persistence: none.

Dependencies and integration: called by `remote_daemon.go`.

Risks: absence of process-group/death-signal semantics means cleanup relies on explicit supervisor stop/kill paths.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/utils_windows.go -->
