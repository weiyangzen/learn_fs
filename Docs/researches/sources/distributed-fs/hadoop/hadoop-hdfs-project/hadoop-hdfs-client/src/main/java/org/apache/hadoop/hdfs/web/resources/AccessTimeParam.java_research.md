# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AccessTimeParam.java

## Purpose

`AccessTimeParam` models the WebHDFS `accesstime` query parameter for `SETTIMES`.

## Important APIs, Types, And Functions

It extends `LongParam`, defines `NAME = "accesstime"` and `DEFAULT = "-1"`, and has constructors from `Long` or `String`.

## Control Flow

The `Long` constructor permits values from `-1` upward. The `String` constructor parses through the domain. `getName` returns the query key.

## State And Persistence

State is the inherited immutable parsed parameter value. No persistence exists.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.setTimes` with `ModificationTimeParam`.

## Risks

Negative values other than `-1` are rejected by the inherited range. Server semantics must continue treating `-1` as unchanged/default.

## Test Signals

Tests should parse valid timestamps, `-1`, invalid negatives, and query serialization.
