# sources/cloud-native/cri-o/server/listen_windows.go

Purpose: Windows listener wrapper that maps CRI-O's Unix-style listener request to Windows named pipes.

Important APIs and functions: `Listen(network, address)` calls `winio.ListenPipe` when `network == "unix"`; otherwise it delegates to `net.Listen`.

Control flow: simple network switch with no cleanup or validation.

State and persistence: creates Windows named pipe listeners or normal network listeners.

Dependencies and integration: depends on `github.com/Microsoft/go-winio`; keeps the public `Listen` API consistent across platforms.

Risks: callers using `"unix"` on Windows get named-pipe semantics, so permissions and address syntax differ from Unix sockets.

Test signals: no Windows-specific tests in this subset; compile and platform CI are the likely guard.
