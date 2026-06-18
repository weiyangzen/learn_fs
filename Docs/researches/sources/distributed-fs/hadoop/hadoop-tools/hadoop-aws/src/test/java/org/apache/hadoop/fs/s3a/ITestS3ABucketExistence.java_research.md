# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABucketExistence.java

Purpose: verifies S3A bucket existence probing modes and error behavior against a random non-existent bucket.

Important APIs/types/functions: extends `AbstractS3ATestBase`; creates `randomBucket` and `s3a://random-bucket-.../` URI. `createConfiguration()` skips unless the endpoint is AWS. `createConfigurationWithProbe(int)` disables FS caching, removes endpoint/region/probe overrides, sets probe value and region. `expectUnknownStore()` helpers intercept `UnknownStoreException`. Access-point tests configure ARN bucket options and `AWS_S3_ACCESSPOINT_REQUIRED`.

Control flow: probe 0 initializes FS without init-time failure, root exists/status succeeds, but object operations are expected to fail with unknown store except `isFile()` false. Probe 1/2 fail at FS creation; probe 3 allows root status. Negative probe expects `IllegalArgumentException`. Access point required path validates missing-ARN error then unknown store when ARN is present.

State and persistence: creates/uses a secondary `FileSystem fs` for nonexistent bucket and cleans it up after each test.

Dependencies and integration: S3A probing constants, network endpoint detection, access point ARN options, exception translation, and filesystem caching controls.

Risks: tests require AWS endpoint behavior and credentials sufficient to distinguish no-such-bucket from access denial; otherwise some paths skip.

Test signals: integration coverage for bucket probe modes, root special cases, access point validation, and unknown-store propagation.
