# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ILoadTestS3ABulkDeleteThrottling.java

Purpose: parameterized load/scale test that stresses S3 bulk-delete throttling behavior by issuing many concurrent `removeKeys` calls with different bulk page sizes and AWS internal throttling settings.

Important APIs/types/functions: extends `S3AScaleTestBase` and is tagged `@LoadTest`/`@ScaleTest`; parameter tuples cover throttle on/off and default/max delete page sizes. It uses a 20-thread Hadoop executor, `ExecutorCompletionService`, `ObjectIdentifier` lists, `Csvout`, `NanoTimerStats`, and an `Outcome` record writer.

Control flow: configuration removes relevant overrides, sets `EXPERIMENTAL_AWS_INTERNAL_THROTTLING`, `BULK_DELETE_PAGE_SIZE`, user agent, and disables FS caching. Setup requires multi-delete, creates a local results directory, and verifies page size. Ordered tests reset static throttle state, run delete stress, then optionally sleep/recovery-delete if throttling was observed. `deleteFiles` builds one synthetic key list, submits request tasks, each task wraps `fs.removeKeys` in an audit span, records success/failure/timing, writes TSV output, and logs aggregate success/throttle stats and TPS.

State and persistence: no test objects need to exist for deletion keys; result CSV/TSV files are written under the local test dir. Static `testWasThrottled` coordinates recovery sleep, though this file records exceptions locally and does not visibly set the flag.

Dependencies/integration: S3A bulk delete, AWS throttling config, audit spans, local test directory utilities, Guava thread factory, and scale timing stats.

Risks: expensive and potentially disruptive to a bucket/shard; local result files accumulate; static throttle flag behavior may be incomplete; concurrency/timing can be environment-dependent.

Test signals: completion without unhandled failures, per-request outcome rows, aggregate throttle counts, and logged throughput.
