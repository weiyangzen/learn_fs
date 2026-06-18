## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/manager.go

Purpose: provides a reusable non-HTTP facade for S3 Tables operations, aimed at shell/admin tooling and the Iceberg catalog while reusing the HTTP handler implementation.

Important APIs: `Manager`, `NewManager`, `SetRegion`, `SetAccountID`, `SetDefaultAllow`, `SetTrusted`, `Execute`, `decodeS3TablesHTTPResponse`, `ManagerClient`, and `NewManagerClient`.

Control flow: `Execute` marshals a request object, builds an in-memory POST with `application/x-amz-json-1.1` and `X-Amz-Target: S3Tables.<operation>`, optionally injects identity headers/context, sends it through `HandleRequest` using `httptest.ResponseRecorder`, then decodes either JSON response or `S3TablesError`.

State and dependencies: owns an embedded `S3TablesHandler`. `ManagerClient` adapts `filer_pb.SeaweedFilerClient` to the local `FilerClient` callback interface. No persistence beyond handler configuration.

Risks: reusing HTTP machinery means manager callers inherit routing/auth semantics and error encoding. Identity name alone is treated as an authenticated principal unless manager is trusted or admin. `manager_test.go` covers the key authorization boundaries.
