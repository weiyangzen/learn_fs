# sources/cloud-native/containerd/cmd/containerd/command/notify_no_systemd.go

Purpose: supplies no-op systemd notification functions for Linux builds compiled with `no_systemd`.

Important APIs/functions: `notifyReady(context.Context) error` and `notifyStopping(context.Context) error` both return nil.

Control flow: daemon startup and shutdown can call these functions unconditionally without linking `go-systemd`.

State and persistence: none.

Dependencies/integration: selected by build tag `linux && no_systemd`; keeps the same function signatures as systemd-enabled builds.

Risks: service managers expecting readiness/stopping notifications will not receive them in this build variant.

Test signals: no local tests; behavior is trivial and build-tag selected.
