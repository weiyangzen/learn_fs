<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/client.go

Purpose: minimal Docker API client for BuildKit integration tests, with local socket/npipe support and raw connection dialing.

Important APIs and types: `Client`, constants `DummyHost` and `DefaultVersion`, `CheckRedirect`, `NewClientWithOpts`, `Close`, `ParseHostURL`, `dialerFromTransport`, and `Dialer`.

Control flow: `NewClientWithOpts` parses the platform default host, creates a default HTTP client/transport, applies functional options, records base transport, and defaults request scheme based on TLS config. `ParseHostURL` validates `proto://addr` style hosts and extracts TCP base paths. `Dialer` returns a raw connection function using configured transport dialer, unix socket, npipe, TLS dialer, or plain net dialer.

State and persistence: holds connection configuration, API version, HTTP client, and base transport. `Close` closes idle connections.

Dependencies and integration: integrates with socket configuration files in the same package, test dockerd daemon helpers, and Docker API request/hijack helpers.

Risks: intentionally minimal compared to full Docker client. `DummyHost` is used to satisfy Go HTTP requirements for local transports. Redirect policy rejects non-GET redirects to avoid method rewrite surprises.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client.go -->
