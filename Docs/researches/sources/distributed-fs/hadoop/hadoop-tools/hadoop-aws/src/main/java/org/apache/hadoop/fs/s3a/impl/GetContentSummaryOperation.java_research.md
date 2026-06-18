<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/GetContentSummaryOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/GetContentSummaryOperation.java

## Purpose

`GetContentSummaryOperation` computes S3A content summaries optimized for object-store listings and exposes IO statistics for the listing work.

## Important APIs, Types, and Functions

It extends `ExecutingStoreOperation<ContentSummary>` and implements `IOStatisticsSource`. Key methods are `execute()`, `getDirSummary()`, `buildDirectorySet()`, `probePathStatusOrNull()`, and callback methods for status probes and recursive listings.

## Control Flow

Execution first probes for a file; files return a one-file summary. Directories are recursively listed. The operation counts file lengths and file count, tracks all inferred ancestor directories in sets, aggregates iterator IO statistics, and returns a `ContentSummary` with directory count equal to base directory plus inferred directories.

## State and Persistence Behavior

State includes target path, callbacks, and an `IOStatisticsSnapshot` aggregated during execution. No persisted state is written.

## Dependencies and Integration Points

It depends on S3A status/listing callbacks, `S3ALocatedFileStatus`, Hadoop `ContentSummary`, and IO statistics retrieval from iterators.

## Risks and Edge Cases

It only probes file status initially; missing paths fall through to directory listing, which must raise not found. Directory inference is needed because S3 may not store every ancestor marker. Large trees can grow the directory sets substantially.

## Test Signals

Cover file summary, empty directory, nested directories without markers, explicit directory markers, missing path, iterator IO stats aggregation, duplicate sibling parent optimization, and recursive listing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/GetContentSummaryOperation.java -->
