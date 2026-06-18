<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpPutFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpPutFailedException.java

## Purpose

`HttpPutFailedException` reports a failed HTTP PUT while preserving the response code.

## Important APIs and types

It extends `IOException`, stores an integer `responseCode`, and exposes `getResponseCode`.

## Control flow

Callers construct it with the already-known message and status code after a failed PUT operation.

## State and persistence behavior

State is limited to the exception message and response code. It is not persisted.

## Dependencies and integration points

It integrates with HDFS HTTP upload/checkpoint/image transfer paths that use PUT semantics.

## Risks and edge cases

The exception does not include response body, headers, or URL unless the caller includes those in the message.

## Test signals

Tests should verify response-code preservation and caller behavior for retryable and non-retryable HTTP status codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpPutFailedException.java -->
