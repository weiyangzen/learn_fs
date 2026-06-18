# sources/distributed-fs/ipfs-kubo/test/cli/rpc_get_output_test.go

Purpose: specifically guards `ipfs get` RPC output `Content-Type` headers for tar and gzip transport formats.

Important APIs and functions: `TestRPCGetContentType` starts an offline daemon, adds one string, then table-drives raw HTTP POST requests to `/api/v0/get` with query combinations for default, `archive=true`, `compress=true`, and `archive=true&compress=true`.

Control flow: each subtest builds the full RPC URL, posts with no body, requires status 200, and compares the `Content-Type` header. Default and archive output are expected to be `application/x-tar`; compressed variants are expected to be `application/gzip`.

State and persistence: only one added CID is needed. The test observes live HTTP RPC output and does not inspect extracted bytes or persisted state.

Dependencies and integration points: integrates `get` command option parsing, RPC response headers, archive/gzip output selection, and the HTTP API transport. The test references the long-standing content-type issue it protects.

Risks and test signals: header comparisons are exact and may need coordinated updates if MIME decisions change. Failures signal that consumers of RPC `get` can no longer infer stream format from headers.
