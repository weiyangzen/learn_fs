<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/httpserver/server.go -->
# sources/cloud-native/buildkit/util/testutil/httpserver/server.go

Purpose: configurable HTTP test server with route responses and request statistics.

Important APIs and types: `TestServer`, `NewTestServer`, `SetRoute`, `ServeHTTP`, `Stats`, `Response`, `Stat`, and `Request`.

Control flow: server looks up a route by path, records request stats, sets response headers for last-modified/content-encoding/content-disposition/etag, handles matching `If-None-Match` with 304 and cached count, then writes status 200 and content. `Stats` returns a snapshot copy of the stat struct.

State and persistence: in-memory route map and stats map protected by mutex. Request headers are cloned per recorded request.

Dependencies and integration: uses `httptest.Server`; useful for source fetching/cache tests.

Risks: `Stats` returns a shallow copy; the `Requests` slice backing array is shared. Route map provided to constructor is retained, so external mutation is possible unless callers avoid it. `io.Copy` write errors are ignored.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/httpserver/server.go -->
