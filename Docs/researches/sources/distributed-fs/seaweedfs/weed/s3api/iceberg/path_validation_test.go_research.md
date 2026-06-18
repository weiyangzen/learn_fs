# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation_test.go

Purpose: tests for Iceberg path traversal defense.

Important tests: `TestIsValidTablePath` accepts normal paths and rejects `..`, `.`, and backslash forms. `TestValidateRequestPath_RejectsTraversal` builds a mux router with `SkipClean(true)` and checks clean routes pass while `..` in prefix/namespace/table, bare `.`, unit-separator namespace traversal, and leading/trailing/consecutive separators are rejected before the handler runs. `TestValidateRequestPath_RejectsEmptyCapturedVars` directly sets empty mux vars to verify defense-in-depth. `TestIsValidNameSegment` documents allowed dot-containing names and rejected separators/NUL.

State and dependencies: local httptest routers/recorders and mux URL vars. Integration point is `Server.RegisterRoutes`, where the middleware is installed after logging and before authenticated handlers. Risks covered are bucket escape and route-variable collapse into the same namespace. Test signal is strong for HTTP middleware behavior and helper boundaries.
