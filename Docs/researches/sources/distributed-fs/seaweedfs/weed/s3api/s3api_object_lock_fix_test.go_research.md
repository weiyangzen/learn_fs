# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lock_fix_test.go

Purpose: this regression test documents a Veeam interoperability fix for Object Lock configuration detection. The bug was that a bucket entry with nil extended attributes could be treated as missing Object Lock configuration before checking whether Object Lock was actually enabled, causing clients to conclude Object Lock was unsupported.

Important APIs/types/functions: `TestVeeamObjectLockBugFix` builds `BucketConfig` values around `filer_pb.Entry.Extended` and checks the same enabled-flag logic used by object-lock configuration handling. It relies on `s3_constants.ExtObjectLockEnabledKey` and `s3_constants.ObjectLockEnabled`.

Control flow: the first subtest models a bucket with `Extended: nil` and verifies the enabled calculation safely returns false rather than panicking or misclassifying. The second sets the extended flag to string `"true"` and expects enabled. The third sets the flag to the canonical `ObjectLockEnabled` constant and expects enabled.

State and persistence behavior: the test models bucket-level persisted metadata as extended attributes on the bucket entry. It does not call the actual handler or mutate storage. The persistence contract under test is that both legacy boolean `"true"` and canonical enabled values are recognized, while nil metadata means not enabled.

Dependencies and integration points: this test is adjacent to `GetObjectLockConfigurationHandler`, bucket config parsing, `isObjectLockEnabled`/availability helpers, object-lock write validation in `put.go`, and retention handlers. It is specifically motivated by backup software probing bucket object-lock support.

Risks: because the test duplicates detection logic instead of invoking the production handler/helper, it can drift if production logic changes. It is useful as documentation of expected semantics but weaker than an integration test that calls the handler with bucket cache entries for nil, false, true, and canonical enabled cases.

Test signals: focused signal for nil extended attributes and dual accepted enabled encodings. It protects against reintroducing `NoSuchObjectLockConfiguration` behavior for enabled buckets whose metadata representation is sparse or legacy.
