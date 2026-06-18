# sources/cloud-native/cri-o/internal/dbusmgr/dbusmgr.go

Purpose: manages a shared systemd D-Bus connection with rootless/root selection and automatic reconnect on closed connections.

Important APIs/types/functions: package globals `dbusC`, `dbusMu`, `dbusInited`, `dbusRootless`; `DbusConnManager`; `NewDbusConnManager`, `GetConnection`, `newConnection`, `RetryOnDisconnect`, and `resetConnection`.

Control flow: construction normalizes rootless=false when UID is 0, prevents mixing root and rootless managers in one process, and marks global initialization. `GetConnection` uses double-checked locking to lazily create the shared connection. `newConnection` selects user or system systemd D-Bus. `RetryOnDisconnect` repeatedly obtains a connection, retries immediately on `EAGAIN`, resets and reconnects on `dbus.ErrClosed`, and returns other errors.

State and persistence behavior: global in-memory shared connection and mode flags. No persistent files.

Dependencies/integration points: Linux build only. Uses coreos go-systemd D-Bus, godbus errors, OS UID, and `newUserSystemdDbus` from `user.go`. Used by systemd cgroup manager code.

Risks: process-wide singleton panics if root and rootless modes are mixed. `RetryOnDisconnect` can loop indefinitely on persistent `EAGAIN`. Uses `context.TODO` for system connection.

Test signals: no direct tests in this subset.
