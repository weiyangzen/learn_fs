<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/PublicDatasetTestUtils.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/PublicDatasetTestUtils.java


## Purpose
Utility centralizing public S3 dataset paths and configuration keys used by S3A tests.


## Important APIs, Types, and Functions
PublicDatasetTestUtils defines defaults for requester-pays, many-objects, ORC, and external gzipped data; methods include getOrcData(), getExternalData(), requireAnonymousDataPath(), requireDefaultExternalDataFile(), isUsingDefaultExternalDataFile(), requireDefaultExternalData(), getBucketPrefixWithManyObjects(), getRequesterPaysObject(), and fetchFromConfig().


## Control Flow
Callers obtain Paths or URI strings from configuration with defaults. require* methods use assumptions to skip tests when configured values are empty or not the expected default.


## State and Persistence Behavior
No persistent state beyond constants. Methods may use and semantically depend on mutable Configuration, but only read from it here.


## Dependencies and Integration Points
Depends on Hadoop Configuration/Path, S3ATestConstants, S3ATestUtils.assume(), and AssertJ assumptions.


## Risks and Test Signals
Risks are public dataset movement, requester-pays costs, or endpoint changes. Signals standardize external data contracts so tests fail/skip consistently rather than embedding stale paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/PublicDatasetTestUtils.java -->
