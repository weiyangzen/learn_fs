# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/nydusd.go

Purpose: creates configuration for and controls a `nydusd` process mounted by the checker.

Important APIs and flow: `NydusdConfig` carries backend, cache, socket, mount, bootstrap, mode, prefetch, and digest validation settings. `makeConfig` renders a JSON template, defaulting empty backend to localfs `{"dir": "/fake"}` and requiring explicit config for nonempty backend type. `checkReady` creates an HTTP client over a Unix socket and polls `/api/v1/daemon` until JSON state is `RUNNING` or context cancellation. `NewNydusd` writes config and returns a wrapper. `Mount` first calls silent `Umount`, starts `nydusd` with config, mountpoint, bootstrap, apisock, and warn logging, then races process exit, readiness, and a 30 second timeout. `Umount` shells out to `umount <mountpath>` if the mount path exists.

State and persistence: writes config files, starts long-lived external process, uses Unix socket HTTP, and changes kernel mount state.

Dependencies and integration: integrates checker rootfs validation with real `nydusd`. Uses `text/template`, `net/http`, Unix socket dialing, `exec`, and logrus.

Risks and test signals: readiness goroutine spins without sleep on connection failure, which can consume CPU during startup. `defer resp.Body.Close()` inside a loop delays closes until goroutine return. Runtime depends on `umount` and `nydusd` availability.
