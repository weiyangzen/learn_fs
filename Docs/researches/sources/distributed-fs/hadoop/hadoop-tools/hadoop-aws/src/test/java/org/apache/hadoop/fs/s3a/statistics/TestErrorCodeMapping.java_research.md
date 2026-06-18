<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/TestErrorCodeMapping.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/TestErrorCodeMapping.java


## Purpose
Parameterized unit test for mapping HTTP status codes from AWS SDK failures to S3A statistic names.


## Important APIs, Types, and Functions
TestErrorCodeMapping defines params(), constructor fields code/name, and testMapping(). It targets StatisticsFromAwsSdkImpl.mapErrorStatusCodeToStatisticName().


## Control Flow
JUnit parameterization feeds representative 2xx/3xx/4xx/5xx codes. The test asserts only selected errors map to specific HTTP_RESPONSE_* counters; 404 and non-error statuses map to null, while GCS 429 maps to HTTP_RESPONSE_503.


## State and Persistence Behavior
No external state; all state is constructor parameters for the current test instance.


## Dependencies and Integration Points
Depends on StatisticsFromAwsSdkImpl, InternalConstants status code constants, StoreStatisticNames, AssertJ, and JUnit parameterized class support.


## Risks and Test Signals
Risks are provider-specific status mapping changes. Signals protect cost/statistic categorization for error counters.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/TestErrorCodeMapping.java -->
