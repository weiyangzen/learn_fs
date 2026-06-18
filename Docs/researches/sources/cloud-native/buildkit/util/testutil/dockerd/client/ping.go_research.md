<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/ping.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/ping.go

Purpose: implements Docker daemon ping for the test client.

Important APIs and types: `PingResponse` and `Client.Ping`.

Control flow: builds a HEAD request to non-versioned `/_ping`, sends it, drains/closes the response body, and converts non-2xx/3xx responses through `checkResponseErr`.

State and persistence: no state beyond network request.

Dependencies and integration: uses `buildRequest`, `doRequest`, and response error helpers in the same package.

Risks: does not perform API version negotiation; intentionally hits base ping endpoint.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/ping.go -->
