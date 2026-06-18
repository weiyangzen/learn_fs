<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_windows.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_windows.go

Purpose: Windows named-pipe transport support for the test Docker client.

Important APIs and types: `configureUnixTransport`, `configureNpipeTransport`, and `DialPipe`.

Control flow: unix transport returns unsupported. npipe transport disables compression and installs a `go-winio` pipe dialer. `DialPipe` delegates to `winio.DialPipe` with timeout.

State and persistence: mutates an `http.Transport`.

Dependencies and integration: uses Microsoft `go-winio` and platform build tags.

Risks: named pipe dialing depends on Windows privileges and daemon availability.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets_windows.go -->
