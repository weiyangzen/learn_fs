# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/ConcatSourcesParam.java

## Purpose

`ConcatSourcesParam` serializes the `sources` query parameter for WebHDFS concat operations.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "sources"`, constructors from raw string and `Path[]`, helper `paths2String`, and `getAbsolutePaths`.

## Control Flow

Path arrays are converted to comma-separated URI paths; null or empty arrays become empty string. `getAbsolutePaths` splits the stored string on commas.

## State And Persistence

Only inherited string value exists.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.concat`.

## Risks

Comma-separated encoding assumes paths cannot contain unescaped commas in a way that survives URI path conversion. Empty source arrays serialize as empty rather than being rejected locally.

## Test Signals

Tests should cover multiple paths, empty/null arrays, absolute path preservation, comma-containing paths if supported, and server-side concat validation.
