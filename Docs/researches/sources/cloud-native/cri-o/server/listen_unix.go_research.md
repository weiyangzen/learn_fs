# sources/cloud-native/cri-o/server/listen_unix.go

Purpose: non-Windows listener wrapper for CRI-O server sockets.

Important APIs and functions: `Listen(network, address)` directly delegates to `net.Listen`.

Control flow: no socket cleanup or address translation is performed here.

State and persistence: creates operating-system listeners, including Unix domain sockets when requested.

Dependencies and integration: used by server startup code that expects a platform-specific listener abstraction.

Risks: stale Unix socket cleanup must happen before calling this function; it will fail if the address is already bound.

Test signals: `listen_unix_test.go` confirms successful Unix socket bind and failure on a second bind to the same path.
