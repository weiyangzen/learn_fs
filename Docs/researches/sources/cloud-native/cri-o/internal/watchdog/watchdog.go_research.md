# sources/cloud-native/cri-o/internal/watchdog/watchdog.go

Purpose: implements CRI-O's systemd watchdog notification loop with pluggable health checks.

Important APIs/types/functions: `Watchdog` struct, `HealthCheckFn`, `New`, `Start`, `Notifications`, and `runHealthCheckers`. `minInterval` requires a watchdog timeout greater than one second.

Control flow: `Start` asks systemd for the watchdog timeout, returns nil when disabled, rejects too-small intervals, halves the interval, and starts a goroutine with `wait.Until`. Each tick runs health checkers sequentially; on success it uses two-step exponential backoff to call `Notify(SdNotifyWatchdog)`. Notify errors are retried; unsupported notification returns a terminal backoff error for that tick. Notifications are counted for every notify attempt.

State and persistence: stores health checkers, backoff config, injected `Systemd`, and an atomic notification-attempt counter. No durable state.

Dependencies/integration: uses `github.com/coreos/go-systemd/v22/daemon`, Kubernetes `wait`, CRI-O internal logging, and `Systemd` abstraction. Higher-level server startup can instantiate this with health probes.

Risks: health checkers run serially and one failure suppresses later checks and notification. The goroutine is asynchronous; `Start` returning nil does not mean a notification succeeded. `Notifications` counts failed attempts too. Too-small systemd intervals fail startup for watchdog setup.

Test signals: tests cover success, retry, unsupported notify, unhealthy checker suppression, disabled watchdog, `WatchdogEnabled` error, and too-low interval.
