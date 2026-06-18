## sources/distributed-fs/ipfs-kubo/test/sharness/t0230-channel-streaming-http-content-type.sh

Purpose: verifies HTTP API streaming response content type and CORS headers for channel-streaming commands.

Important APIs and helpers: defines `test_ls_cmd`, uses `ipfs add -r`, API endpoint `http://$API_ADDR/api/v0/refs?...&stream-channels=true`, `curl -X POST -i`, `grep`, `test_cmp`, and daemon lifecycle helpers.

Control flow and state: creates a small test directory, adds it, calls the refs API with channel streaming enabled, and compares HTTP headers for status, allowed CORS headers, content type, and stream output behavior. The helper is run for relevant command variants.

Dependencies and integration points: covers API command HTTP envelope, streaming channel negotiation, CORS header generation, and refs traversal over API.

Risks and test signals: catches browser/API compatibility regressions caused by wrong content type or missing stream headers. Passing is exact header comparison against the expected HTTP response prefix.
