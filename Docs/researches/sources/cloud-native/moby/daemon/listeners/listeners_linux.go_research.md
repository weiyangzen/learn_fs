## sources/cloud-native/moby/daemon/listeners/listeners_linux.go

Purpose: Initializes Linux daemon API listeners for systemd socket activation, TCP, and Unix socket protocols.

Important APIs: `Init(proto, addr, socketGroup string, tlsConfig *tls.Config)` dispatches on `fd`, `tcp`, and `unix`. `listenFD(addr string, tlsConfig *tls.Config)` loads systemd-activated listeners, optionally wraps TLS listeners, returns all listeners for empty or `*`, or selects one listener by numeric fd address.

Control flow and state: TCP uses `sockets.NewTCPSocket`. Unix resolves a GID with `lookupGID`; if the default group is missing it logs a warning and falls back to current GID, but non-default explicit group errors are returned. After `sockets.NewUnixSocket`, it asks `homedir.StickRuntimeDirContents` to protect sockets under `XDG_RUNTIME_DIR`. `listenFD` validates listener presence, parses fd numbers relative to systemd fd 3, closes unselected listeners, and returns the requested one.

Dependencies and integration points: Integrates with `go-systemd/activation`, Docker go-connections sockets, TLS, homedir runtime-dir sticky-bit handling, and containerd logging.

Risks: fd selection error messages are critical for service startup diagnosis. Closing unselected activated listeners must not close the selected fd. Unix socket permissions depend on group lookup and filesystem behavior.

Test signals: No direct tests in this subset.
