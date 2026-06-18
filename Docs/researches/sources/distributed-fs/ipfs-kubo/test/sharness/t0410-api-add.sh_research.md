## sources/distributed-fs/ipfs-kubo/test/sharness/t0410-api-add.sh

Purpose: narrow regression test that the HTTP API `add` command response includes a `Size` field.

Important commands and control flow: initializes and launches a daemon, pipes `hi` as multipart file data to `http://localhost:$API_PORT/api/v0/add`, and greps for `"Size": "11"` in the JSON response.

State and persistence: the uploaded data is added to the repo through the API; no further cleanup-specific behavior is asserted.

Dependencies and integration points: depends on HTTP multipart handling, UnixFS add response formatting, `curl`, and daemon lifecycle.

Risks and test signals: catches response schema regressions for API clients relying on `Size`. Exact size includes multipart/add semantics and may change if response accounting changes.
