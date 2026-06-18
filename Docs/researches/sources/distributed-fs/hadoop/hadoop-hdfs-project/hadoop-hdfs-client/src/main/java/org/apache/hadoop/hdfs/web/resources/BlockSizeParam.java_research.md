# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BlockSizeParam.java

## Purpose

`BlockSizeParam` represents optional WebHDFS `blocksize` values for file creation.

## Important APIs, Types, And Functions

It extends `LongParam`, defines `NAME = "blocksize"` and default `NULL`, supports Long/String constructors, and adds `getValue(Configuration)`.

## Control Flow

Explicit values must be at least 1. If unset, `getValue(conf)` returns `dfs.blocksize` from configuration with default fallback.

## State And Persistence

Only the parsed value is stored. Configuration is consulted on demand.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.create` and `createNonRecursive`.

## Risks

Differences between omitted query parameters and explicit default block size can affect server-side defaults. Very large values depend on `LongParam` and server validation.

## Test Signals

Tests should cover null default resolution, invalid zero/negative values, string parsing, and create URL serialization.
