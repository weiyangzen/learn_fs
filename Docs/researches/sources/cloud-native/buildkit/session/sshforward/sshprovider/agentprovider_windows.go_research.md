## sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_windows.go

Purpose: implements Windows-specific SSH agent discovery and named-pipe dialing.

Important APIs/types/functions: `getFallbackAgentPath` checks `\\.\pipe\openssh-ssh-agent` using `windows.FindFirstFile` and returns it if available. `isWindowsPipePath` detects named pipe paths with slash/backslash tolerant regex. `getWindowsPipeDialer` returns a `socketDialer` using `windowsPipeDialer` when a path is a pipe. `windowsPipeDialer` calls `winio.DialPipe`.

Control flow: fallback avoids `os.Stat` because Windows named pipes do not behave like normal filesystem entries. Config path classification in `agentprovider.go` calls `getWindowsPipeDialer` before `os.Stat`, so pipe paths can bypass Unix socket/file logic.

State and persistence: no durable state. The only resource is the find handle, which is closed.

Dependencies and integration points: depends on Microsoft go-winio and x/sys/windows; selected only on Windows builds. It lets BuildKit support OpenSSH agent forwarding on Windows clients.

Risks and test signals: regex pipe detection must handle path variants; false negatives would fall through to `os.Stat`. The fallback only supports the standard OpenSSH pipe. No Windows-specific test is in this subset.
