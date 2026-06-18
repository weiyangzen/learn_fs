<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_windows.go -->
# sources/cloud-native/moby/client/client_windows.go

Purpose: supplies Windows-specific daemon connection defaults and named-pipe dialing.

Important APIs/functions: `DefaultDockerHost = "npipe:////./pipe/docker_engine"` and `dialPipeContext`, which delegates to `winio.DialPipeContext`.

Control flow and dependencies: minimal platform-specific implementation guarded by build tags. It imports `github.com/Microsoft/go-winio`.

State and integration behavior: no persistence. `client.go` uses this default host on Windows and calls `dialPipeContext` when the configured protocol is `npipe`.

Risks and test signals: compatibility depends on build tags and named-pipe address formatting. Cross-platform tests around `ParseHostURL` and request host behavior indirectly protect this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_windows.go -->
