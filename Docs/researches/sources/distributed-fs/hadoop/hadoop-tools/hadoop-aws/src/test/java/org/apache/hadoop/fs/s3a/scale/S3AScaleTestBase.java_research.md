<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/S3AScaleTestBase.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/S3AScaleTestBase.java


## Purpose
Common base class for S3A scale tests that centralizes configuration creation, scale enablement, operation counts, timeouts, and gauge lookup.


## Important APIs, Types, and Functions
S3AScaleTestBase defines _1KB/_1MB, setup(), demandCreateConfiguration(), final createConfiguration(), overridable createScaleConfiguration(), getTestPath(), getOperationCount(), getTestTimeoutSeconds(), getTestTimeoutMillis(), gaugeValue(), isEnabled(), and isParallelExecution().


## Control Flow
Configuration is lazily created before normal JUnit setup so timeout calculation can read scale properties early. setup() initializes a shared test path, logs operation count, and skips unless scale tests are enabled. Subclasses customize only createScaleConfiguration().


## State and Persistence Behavior
Instance state is the cached Configuration, enabled flag, and testPath. The design intentionally guards against subclasses overriding createConfiguration() and breaking early timeout/config initialization.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, S3ATestUtils property helpers/assume(), IOStatistics gauge lookup, S3ATestConstants, and ScaleTest tagging.


## Risks and Test Signals
Risks are Java constructor/override ordering and stale configuration if subclasses expect repeated creation. Test signals are indirect: all scale tests rely on correct enablement, timeout, and operation-count behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/S3AScaleTestBase.java -->
