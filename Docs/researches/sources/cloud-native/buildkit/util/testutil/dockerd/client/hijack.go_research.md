<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/hijack.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/hijack.go

Purpose: implements Docker-style HTTP connection hijacking/upgrade for test client raw streams.

Important APIs and types: `DialHijack`, `setupHijackConn`, `CloseWriter`, `hijackedConn`, and `hijackedConnCloseWriter`.

Control flow: builds a POST request with `Connection: Upgrade` and `Upgrade: proto`, dials the daemon, enables TCP keepalive when applicable, writes the request through a lightweight round tripper, requires `101 Switching Protocols`, and returns the raw connection. If HTTP buffered data remains, wraps the connection so reads drain the buffered reader, preserving `CloseWrite` when supported.

State and persistence: transient network connection only.

Dependencies and integration: uses the client `Dialer`, Go HTTP read/write primitives, and is intended for Docker API endpoints that hijack connections.

Risks: caller owns returned connection lifecycle. The `meta` parameter is unused. Non-101 responses close their body and return an error.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/hijack.go -->
