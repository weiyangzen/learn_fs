<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/options.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/options.go

Purpose: functional option support for configuring the test Docker client.

Important APIs and types: `Opt` and `WithHost`.

Control flow: `WithHost` parses the supplied host, updates client host/proto/addr/basePath, and reconfigures the existing HTTP transport for the selected protocol.

State and persistence: mutates a `Client` during construction.

Dependencies and integration: uses `ParseHostURL` and `configureTransport`.

Risks: fails if the client transport is not `*http.Transport`; options must be applied before tracing/wrapping changes the transport type.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/options.go -->
