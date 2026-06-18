# sources/distributed-fs/seaweedfs/weed/s3api/cors/cors_test.go

Purpose: unit tests for pure CORS validation, parsing, matching, evaluation, and header application.

Important tests: `TestValidateConfiguration`, `TestValidateOrigin`, `TestParseRequest`, `TestMatchesOrigin`, `TestMatchesHeader`, `TestEvaluateRequest`, and `TestApplyHeaders`.

Control flow: coverage verifies config validation, origin wildcard constraints, preflight parsing, HTTP/HTTPS exact and wildcard origin matching, protocol mismatch behavior, case-insensitive/prefix header matching, rule evaluation, and httptest response headers.

State and persistence: no persistence; tests compare structs and response headers.

Dependencies and integration points: exercises `cors.go` directly with `httptest`.

Risks and test signals: preflight with forbidden headers returns a response with only `AllowOrigin`, documenting current behavior. XML/JSON marshaling is not covered.
