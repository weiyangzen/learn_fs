# sources/distributed-fs/ipfs-kubo/test/cli/rpc_content_type_test.go

Purpose: verifies RPC `Content-Type` headers for binary and structured endpoints: `dag export`, `block get`, `diag profile`, `name get`, and `routing get`.

Important APIs and functions: tests build raw HTTP POST requests to `node.APIURL() + /api/v0/...` using `http.DefaultClient`. `TestHTTPRPCNameGet` additionally decodes base64 JSON from `routing get` and pipes raw IPNS bytes to `ipfs name inspect`.

Control flow: `TestRPCDagExportContentType` adds content offline and expects `application/vnd.ipld.car`. `TestRPCBlockGetContentType` expects `application/vnd.ipld.raw`. `TestRPCProfileContentType` uses `profile-time=0` and expects `application/zip`. `TestHTTPRPCNameGet` runs online, publishes an IPNS record, fetches it through `name get` as raw bytes with `application/vnd.ipfs.ipns-record`, fetches the same record through `routing get /ipns/<peer>` as JSON, decodes `Extra`, compares bytes, and verifies the record contains the published CID.

State and persistence: content and IPNS records are created in a temporary repo and served through live daemon RPC. No restart persistence is checked.

Dependencies and integration points: integrates HTTP RPC, content serialization, CAR/raw block/profile ZIP/IPNS content types, IPNS publishing, routing records, JSON/base64 transport, and `name inspect`.

Risks and test signals: exact header values are part of the public API. Failures indicate HTTP response metadata regressions, `name get` returning JSON instead of raw record bytes, or `routing get` record content diverging from the dedicated IPNS endpoint.
