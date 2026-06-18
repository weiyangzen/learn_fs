<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets.go

Purpose: protocol-dispatch transport configuration for the test Docker client.

Important APIs and types: `defaultTimeout` and `configureTransport`.

Control flow: dispatches to unix or npipe platform-specific configuration. For other protocols, sets proxy, enables compression, and installs a net dialer with default timeout.

State and persistence: mutates an `http.Transport`.

Dependencies and integration: used by default client construction and `WithHost`.

Risks: subsequent calls overwrite transport dial settings. Compression is disabled only for local transports.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/sockets.go -->
