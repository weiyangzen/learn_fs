<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_unix.go -->
# sources/cloud-native/moby/client/client_unix.go

Purpose: supplies Unix-like platform defaults for daemon connection handling.

Important APIs/functions: `DefaultDockerHost = "unix:///var/run/docker.sock"` and a stub `dialPipeContext` that returns an unsupported-protocol error on non-Windows builds.

Control flow and dependencies: no runtime branching beyond returning an error from `dialPipeContext`; imports `context`, `fmt`, and `net`.

State and integration behavior: no persistence. `client.go` uses `DefaultDockerHost` during `New`, and `dialer` only calls `dialPipeContext` for `npipe`.

Risks and test signals: platform build tags are the key risk. Unix builds must not accidentally attempt Windows named-pipe dialing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_unix.go -->
