# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AllUsersParam.java

## Purpose

`AllUsersParam` models the `allusers` boolean query parameter for operations such as listing trash roots.

## Important APIs, Types, And Functions

It extends `BooleanParam`, defines `NAME = "allusers"` and default `false`, and supports Boolean/String constructors.

## Control Flow

String construction parses case-insensitive `true` or `false`; invalid values fail in `BooleanParam.Domain`.

## State And Persistence

Only inherited parameter value is stored.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.getTrashRoots(boolean allUsers)`.

## Risks

Null string handling is inherited and may fail if callers do not supply the explicit default.

## Test Signals

Tests should cover true/false parsing, invalid values, and query serialization.
