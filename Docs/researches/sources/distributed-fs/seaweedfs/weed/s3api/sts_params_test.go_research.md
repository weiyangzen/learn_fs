## sources/distributed-fs/seaweedfs/weed/s3api/sts_params_test.go

Purpose: tests routing of STS `AssumeRole` POST requests when `Action` appears in the query string or form body.

Important types/tests: `mockIAMIntegration`, `TestSTSAssumeRolePostBody`, and `extractSTSRequestID`.

Control flow: the test constructs a minimal `S3ApiServer` with IAM enabled, registers routes, then sends three POST variants. Query-string `Action=AssumeRole` should hit STS and return missing-parameter 400. Form-body action with bearer auth should route to STS and return service-unavailable 503 instead of IAM 501. SigV4-style form-body action should return 503 or 403, but never 501.

State and dependencies: in-memory IAM identity maps and mock IAM integration; no filer or STS backend. Uses mux routing, request ID headers, and XML error body parsing.

Risks and signals: protects real AWS STS clients that send form-encoded POST bodies. It focuses on routing and request ID propagation, not successful AssumeRole execution.
