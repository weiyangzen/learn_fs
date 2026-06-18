<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/core-site.xml -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/core-site.xml


## Purpose
Test-time Hadoop configuration defaults for hadoop-aws integration tests.


## Important APIs, Types, and Functions
The XML sets hadoop.tmp.dir, bucket-specific endpoint/requester-pays/audit/prefetch properties for public datasets, named regional endpoint aliases, simple security, audit rejection of out-of-span operations, thread-level IOStatistics, low retry counts, and optional auth-keys.xml inclusion.


## Control Flow
Tests load this file as a baseline; per-test code may remove or override properties. The XInclude fallback allows private credentials/bucket bindings outside version control.


## State and Persistence Behavior
State is configuration only, but it controls external S3 endpoints, public buckets, retry behavior, audit behavior, and local temp directories used by many tests.


## Dependencies and Integration Points
Depends on Hadoop Configuration XML parsing, XInclude support, S3A bucket-specific property naming, and PublicDatasetTestUtils defaults.


## Risks and Test Signals
Risks include stale public bucket endpoints, too-low retry counts increasing flakiness, and missing auth-keys.xml for private tests. Signals centralize reproducible integration-test defaults.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/core-site.xml -->
