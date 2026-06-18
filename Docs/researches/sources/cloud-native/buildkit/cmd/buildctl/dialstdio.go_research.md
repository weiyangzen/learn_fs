# Research: sources/cloud-native/buildkit/cmd/buildctl/dialstdio.go

Purpose: implements hidden `buildctl dial-stdio`, used by connection helpers to proxy stdin/stdout to a Unix daemon socket. It is not a normal user command.

Important APIs and flow: `dialStdioAction` dials the configured address with timeout, adapts the connection to half-close interfaces, starts copy goroutines for stdin-to-connection and connection-to-stdout, and returns when either direction finishes according to TTY-friendly rules. `dialer` accepts only `unix://` addresses. `copier` performs `io.Copy` and closes read/write halves with logged close errors.

State and dependencies: no persistence; it moves stream bytes between process stdio and a socket. Dependencies are net dialing, half-close interface support, BuildKit logging, CLI flags, and OS stdio wrappers.

Risks and test signals: non-Unix or connections lacking half-close support fail. Returning immediately when socket-to-stdout finishes avoids hanging on TTY stdin but can hide late stdin errors. There are no direct tests in this subset.
