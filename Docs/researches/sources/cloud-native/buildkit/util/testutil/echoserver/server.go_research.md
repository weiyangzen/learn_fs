<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/echoserver/server.go -->
# sources/cloud-native/buildkit/util/testutil/echoserver/server.go

Purpose: tiny TCP test server that writes a fixed response to every accepted connection.

Important APIs and types: `TestServer`, `NewTestServer`, and `handleConnection`.

Control flow: listens on an ephemeral TCP port, accepts connections in a goroutine until accept fails, and handles each connection by writing the response then closing.

State and persistence: listener remains open until caller closes it through the returned `io.Closer`.

Dependencies and integration: useful for low-level network tests needing deterministic socket response.

Risks: write errors are ignored. The accept loop exits silently on listener close or accept error.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/echoserver/server.go -->
