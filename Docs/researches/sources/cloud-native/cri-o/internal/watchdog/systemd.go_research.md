# sources/cloud-native/cri-o/internal/watchdog/systemd.go

Purpose: wraps go-systemd daemon notification functions behind a small interface for production use and tests.

Important APIs/types/functions: `Systemd` interface with `WatchdogEnabled` and `Notify`; `defaultSystemd`; `DefaultSystemd`; methods delegating to `daemon.SdWatchdogEnabled(false)` and `daemon.SdNotify(false, state)`.

Control flow: direct delegation to systemd helper calls; no retries here.

State and persistence: stateless wrapper. Systemd notification state is external through environment and the notify socket.

Dependencies/integration: consumed by `Watchdog` in `watchdog.go`; test injection swaps it for a gomock implementation.

Risks: passing `false` means the helper checks the current process rather than unset-env behavior. If `NOTIFY_SOCKET` is absent, `Notify` returns unsupported and `Watchdog.Start` handles it.

Test signals: watchdog tests mock this interface rather than invoking real systemd.
