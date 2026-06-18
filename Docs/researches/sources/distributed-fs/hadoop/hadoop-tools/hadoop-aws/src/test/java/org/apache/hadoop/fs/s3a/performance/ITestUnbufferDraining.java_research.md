# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestUnbufferDraining.java

Purpose: integration tests for Classic S3A stream `unbuffer()` behavior when async draining versus aborting is expected.

Important APIs/types/functions: `ITestUnbufferDraining` extends `AbstractS3ACostTest`; `createConfiguration()` disables prefetching, forces `INPUT_STREAM_TYPE=Classic`, removes timeout/connection/read-ahead overrides, and disables checksums. `setup()` creates a separate brittle filesystem with `ASYNC_DRAIN_THRESHOLD=1`, tiny connection pool, low retry/timeouts, and `READAHEAD=1000`. Helpers include `createTestFile`, `lookupCounter`, `assertReadPolicy`, and inner-stream extraction.

Control flow: `testUnbufferDraining` opens near the end of a 50 KB file with file status and low drain threshold, repeatedly seeks/reads/unbuffers, expects Random policy, counts unbuffer events, no aborts, and two policy changes. `testUnbufferAborting` opens with whole-file policy, repeatedly reads/unbuffers at the beginning, expects abort count equal to attempts and Sequential policy retained. Teardown aggregates brittle FS IOStatistics and closes it.

State and persistence: writes a real S3 object for each test and uses a separate filesystem instance whose statistics are inspected after stream close.

Dependencies/integration: Classic `S3AInputStream`, async drain threshold parsing, open-file builder options, IOStatistics propagation, AWS client duration limits.

Risks: intentionally brittle connection/timeouts can make cleanup fragile; behavior is Classic-only and depends on read policy.

Test signals: stream-level and filesystem-level `STREAM_READ_UNBUFFERED`, `STREAM_READ_ABORTED`, and `STREAM_READ_SEEK_POLICY_CHANGED` counters, plus input policy assertions.
