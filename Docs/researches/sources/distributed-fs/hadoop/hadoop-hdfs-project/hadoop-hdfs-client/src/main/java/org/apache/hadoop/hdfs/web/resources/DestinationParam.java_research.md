# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DestinationParam.java

## Purpose

`DestinationParam` carries absolute destination paths for WebHDFS rename and symlink operations.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "destination"`, empty default, static `validate`, constructor, and `getName`.

## Control Flow

Null or empty strings become null. Non-empty values must start with `/`; valid values are normalized through `new Path(str).toUri().getPath()`.

## State And Persistence

Only the validated path string is stored.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.rename`, rename with options, and `createSymlink`.

## Risks

Relative paths are rejected locally. Path normalization may alter raw encoding or redundant separators compared with caller input.

## Test Signals

Tests should cover absolute paths, relative path rejection, empty/null omission, URI normalization, and rename URL serialization.
