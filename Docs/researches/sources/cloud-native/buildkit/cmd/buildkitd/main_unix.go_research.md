# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_unix.go

Purpose: supplies Unix-specific listener, umask, and security descriptor behavior for buildkitd.

Important APIs and flow: init sets process umask to zero and marks fsutil copy accordingly. `listenFD` consumes systemd socket activation listeners, optionally wrapping them with TLS, returns the first listener by default, and rejects explicit fd selection. `getLocalListener` creates a Unix listener through containerd sys helpers and chmods it to `0666`. `groupToSecurityDescriptor` is a no-op on Unix.

State and dependencies: mutates process umask and Unix socket file mode. Depends on systemd activation, containerd sys local listener helpers, filesystem chmod, TLS, and fsutil copy.

Risks and test signals: permissive socket chmod is intentional but security-sensitive and relies on listener path placement. Systemd fd selection is not implemented beyond default first fd. There are no direct tests here.
