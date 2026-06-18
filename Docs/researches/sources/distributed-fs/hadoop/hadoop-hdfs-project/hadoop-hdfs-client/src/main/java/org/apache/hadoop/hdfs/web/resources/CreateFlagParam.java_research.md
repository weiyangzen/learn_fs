# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/CreateFlagParam.java

## Purpose

`CreateFlagParam` serializes an `EnumSet<CreateFlag>` as the WebHDFS `createflag` parameter.

## Important APIs, Types, And Functions

It extends `EnumSetParam<CreateFlag>`, defines `NAME = "createflag"`, default empty string, domain over `CreateFlag.class`, and constructors from enum set or string.

## Control Flow

Enum sets are serialized by the inherited enum-set machinery. Strings are parsed by the domain into the corresponding enum set.

## State And Persistence

Only parsed enum-set value is stored.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.createNonRecursive`; create with overwrite uses `OverwriteParam` instead.

## Risks

Client and server must agree on enum names and delimiter format. Empty defaults must map to server-side create semantics.

## Test Signals

Tests should cover standard create flags, mixed-case string parsing if inherited, empty values, invalid flags, and create URL output.
