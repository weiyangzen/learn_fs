## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/manager_test.go

Purpose: verifies manager authorization behavior before filer mutation by using a sentinel filer client.

Important test assets: `recordingFilerClient` marks whether `WithFilerClient` was reached, and `TestManagerCreateTableBucketAuthorization` exercises authenticated, unauthenticated, trusted, and admin paths.

Control flow: each case configures a `Manager`, executes `CreateTableBucket`, expects an error either from denied authorization or the sentinel filer, and asserts whether reaching the filer matches expected authorization.

State and dependencies: uses fake identity structs, `s3_constants` context helpers, and `testify` assertions. It does not persist anything because the sentinel client returns immediately.

Signals and risks: the test locks down a security-sensitive distinction: default allow only falls open for trusted/anonymous zero-config access, not arbitrary identity names. It also confirms admin principal bypass. Coverage is operation-specific but protects shared manager auth plumbing.
