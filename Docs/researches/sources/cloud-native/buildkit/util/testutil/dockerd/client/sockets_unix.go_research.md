<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_unix.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_unix.go

Purpose: non-Windows unix socket transport support for the test Docker client.

Important APIs and types: `configureUnixTransport`, `configureNpipeTransport`, `DialPipe`, and `maxUnixSocketPathSize`.

Control flow: validates unix socket path length, disables compression, and installs a dialer that ignores request network/address and dials the configured unix socket. npipe configuration and pipe dialing return unsupported errors on non-Windows.

State and persistence: mutates an `http.Transport`.

Dependencies and integration: uses `syscall.RawSockaddrUnix` for max path size and Go net dialers.

Risks: path length validation is platform-derived; overly long generated sockets fail early.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_unix.go -->
