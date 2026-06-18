# sources/cloud-native/nydus-snapshotter/pkg/converter/cs_proxy_unix.go

Purpose: provides a Unix-socket HTTP proxy over a content-store reader so `nydus-image unpack` can stream blob data from an already-packed nydus layer without extracting the data file to disk.

Important APIs and functions: `contentStoreProxy` holds socket path and HTTP server; `setupContentStoreProxy` creates a Unix socket and starts the server; `close` shuts down and removes the socket; `parseRangeHeader` parses byte ranges; `contentProxyHandler` serves HEAD and ranged GET responses from the nydus blob entry or raw reader.

Control flow: setup creates a temp socket path under work dir, removes the temp file, listens on Unix socket, and starts `http.Server` with a handler. The handler initializes by trying to seek `EntryBlob` from the nydus layer; if present, total length is the entry size, otherwise full reader size. HEAD returns content length/type. GET requires a `Range` header after `bytes=`, seeks/skips the internal reader to the requested start, resets when reads move backward, copies the requested length, and sets content headers.

State and persistence: proxy state is in-memory plus a temporary Unix socket file. The handler keeps mutable `dataReader` and `curPos` across requests.

Dependencies and integration points: used by `Unpack` when `UnpackOption.Stream` is true to generate a nydus backend config of type `http-proxy`. It relies on `seekFile` from `convert_unix.go`.

Risks: handler state is not protected for concurrent GET requests, so simultaneous range requests can corrupt `curPos`/reader position. `parseRangeHeader` does not support suffix ranges, open-ended `bytes=start-` fails because empty end is parsed as int, and malformed empty ranges return parse errors. Headers are set after writing body in GET, which can be too late for Go's `net/http` to send them as intended.

Test signals: no direct tests for range parsing or proxy behavior are listed.
