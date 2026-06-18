# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/WebHdfsConstants.java

## Purpose

`WebHdfsConstants` holds scheme and delegation-token-kind constants shared by WebHDFS and SWebHDFS plus a small path-type enum used for JSON status conversion.

## Important APIs, Types, And Functions

Constants are `WEBHDFS_SCHEME`, `SWEBHDFS_SCHEME`, `WEBHDFS_TOKEN_KIND`, and `SWEBHDFS_TOKEN_KIND`. Nested `PathType` has values `FILE`, `DIRECTORY`, `SYMLINK` and `valueOf(HdfsFileStatus)`.

## Control Flow

`PathType.valueOf` checks directory first, symlink second, and otherwise returns file.

## State And Persistence

Only static constants exist. `Text` token-kind instances are shared immutable-ish Hadoop values by convention.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem`, `SWebHdfsFileSystem`, `TokenAspect`, and `JsonUtilClient` status parsing.

## Risks

Changing constant strings breaks filesystem scheme resolution and existing delegation token compatibility. `PathType` ordering must match HDFS status semantics.

## Test Signals

Tests should verify scheme registration, token-kind selection/renewal, and file/directory/symlink JSON status conversions.
