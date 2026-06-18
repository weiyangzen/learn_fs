<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/request.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/request.go

Purpose: central request construction, execution, response error conversion, and response body cleanup for the test Docker client.

Important APIs and types: `buildRequest`, `doRequest`, `checkResponseErr`, `addHeaders`, and `ensureReaderClosed`.

Control flow: `buildRequest` creates a context request, adds headers, sets scheme/host, uses `DummyHost` for unix/npipe Host headers, and defaults body content type. `doRequest` executes the HTTP request and decorates common connection/TLS/permission/npipe errors while preserving context cancellation/deadline sentinels. `checkResponseErr` accepts 2xx/3xx, reads at most 1 MiB of error body, decodes JSON daemon errors when content type is exactly `application/json`, and wraps the message.

State and persistence: no persistent state; drains up to 512 bytes in `ensureReaderClosed` for connection reuse.

Dependencies and integration: used by `Ping` and other client operations. Integrates with local socket/npipe behavior and Docker-style daemon errors.

Risks: JSON detection is strict on content type and misses charset variants. Large error bodies are replaced by a generic message. Windows privilege probing opens `\\.\PHYSICALDRIVE0`.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/request.go -->
