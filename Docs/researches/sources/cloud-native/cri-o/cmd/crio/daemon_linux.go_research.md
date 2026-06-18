# sources/cloud-native/cri-o/cmd/crio/daemon_linux.go

Purpose: Linux systemd readiness notification for the CRI-O daemon.

Important APIs and control flow: `sdNotify` calls `watchdog.DefaultSystemd().Notify(daemon.SdNotifyReady)` and logs a warning on failure. `notifySystem` starts `sdNotify` in a goroutine after the daemon is ready to accept requests.

State and persistence: no persistent state. It sends a readiness message to systemd through the notification socket.

Dependencies and integration: depends on `coreos/go-systemd/daemon`, CRI-O internal watchdog abstraction, and logrus. Called from `main.go` after CRI services are registered and before serving loops fully settle.

Risks: asynchronous notification means failures are only logged and startup continues. Non-systemd environments will warn through the watchdog abstraction.

Test signals: integration/systemd tests or service manager behavior can confirm readiness notification; no direct test in this subset.
