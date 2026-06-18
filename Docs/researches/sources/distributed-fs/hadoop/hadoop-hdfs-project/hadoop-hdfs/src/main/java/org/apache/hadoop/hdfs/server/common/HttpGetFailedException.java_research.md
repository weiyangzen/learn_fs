<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpGetFailedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpGetFailedException.java

## Purpose

`HttpGetFailedException` reports a failed HTTP GET while preserving the server response code.

## Important APIs and types

It extends `IOException`, stores `responseCode`, reads it from a supplied `HttpURLConnection` in the constructor, and exposes `getResponseCode`.

## Control flow

The constructor can itself throw `IOException` if `connection.getResponseCode()` fails. Callers throw it after a non-success GET response and inspect the code for retry or diagnostics.

## State and persistence behavior

State is limited to the exception message and response code. It is not persisted.

## Dependencies and integration points

It integrates with HDFS HTTP transfer/checkpoint/metadata-fetch paths that use `HttpURLConnection`.

## Risks and edge cases

Because response-code retrieval happens during construction, connection state errors can replace the intended higher-level failure. The exception does not store response body or URL.

## Test signals

Tests should cover response-code preservation, constructor propagation when response-code read fails, and caller handling for expected HTTP status codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HttpGetFailedException.java -->
