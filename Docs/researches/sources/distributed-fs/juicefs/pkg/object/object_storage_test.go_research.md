# sources/distributed-fs/juicefs/pkg/object/object_storage_test.go


Purpose: defines the broad shared test suite for `ObjectStorage` implementations.

Important APIs and flow: `testStorage` exercises create idempotence, prefix wrapping, cleanup, Unicode/control-character keys, missing gets, ranged gets, list/list-all ordering, storage-class attrs, overwrite, directory-like keys, multipart upload and optional upload-part-copy, copy, delete idempotence, empty objects, and slash-suffixed keys. Helper `listAll` routes through package `ListAll`; `setStorageClass` configures tiers for stores supporting `SupportTier`. Individual `Test*` functions instantiate many backends, usually guarded by environment variables.

State and persistence: tests mutate either `mem`, temp disk paths, or external object stores. Cleanup is best effort through deletes and deferred calls. `TestMain` can load environment variables from a file.

Dependencies and integration: integrates almost every backend in the package, plus wrappers such as encrypted and sharded stores. Also validates HDFS address parsing, endpoint regexes, marshal/unmarshal, prefix naming, and delimiter traversal.

Risks and gaps: many cloud/provider tests are skipped by default. Shared assertions include provider-specific relaxations, so edge behavior can be tolerated. Some constructor errors are ignored in environment tests. Tests are mutating and require isolated buckets or prefixes.

Test signal: very high as a behavioral contract for object semantics across providers when relevant environments are available.
