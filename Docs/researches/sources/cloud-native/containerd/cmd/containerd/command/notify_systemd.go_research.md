# sources/cloud-native/containerd/cmd/containerd/command/notify_systemd.go

Purpose: implements Linux systemd readiness and stopping notifications for normal Linux builds.

Important APIs/functions: `notifyReady()` sends `SdNotifyReady`; `notifyStopping()` sends `SdNotifyStopping`; `sdNotify()` wraps `daemon.SdNotify(false, state)` and logs whether a notification was actually sent.

Control flow: daemon startup calls ready after server readiness waits complete; signal handling calls stopping before canceling and stopping the server. `SdNotify` may return `notified=false` when `NOTIFY_SOCKET` is absent, which is logged at debug level.

State and persistence: no local persistent state; uses systemd notification socket from environment.

Dependencies/integration: selected by `linux && !no_systemd`; depends on `github.com/coreos/go-systemd/v22/daemon` and containerd logging.

Risks: notification errors are surfaced to callers, but main startup only warns on ready failure while shutdown logs stopping failure and continues.

Test signals: no local tests exercise systemd notification behavior.
