## sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_unix.go

Purpose: supplies non-Windows platform behavior for SSH agent fallback and pipe parsing.

Important APIs/types/functions: `getFallbackAgentPath` returns an error instructing users to set `SSH_AUTH_SOCK`. `getWindowsPipeDialer` always returns nil.

Control flow: there is no branching beyond direct returns. When `AgentConfig.toDialer` sees no path and `SSH_AUTH_SOCK` is empty, this fallback turns that into a user-facing configuration error.

State and persistence: none.

Dependencies and integration points: selected by `//go:build !windows`; complements `agentprovider_windows.go`. Used by `AgentConfig.toDialer`.

Risks and test signals: the fallback does not search common Unix agent paths, so UX depends on environment configuration. `agentprovider_test.go` accepts the exact "invalid empty ssh agent socket" path wrapping triggered by this helper.
