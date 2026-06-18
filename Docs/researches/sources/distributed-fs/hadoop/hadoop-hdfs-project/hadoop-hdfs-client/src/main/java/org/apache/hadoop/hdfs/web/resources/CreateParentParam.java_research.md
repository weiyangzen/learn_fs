# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/CreateParentParam.java

## Purpose

`CreateParentParam` models the WebHDFS `createparent` boolean parameter for create operations.

## Important APIs, Types, And Functions

It extends `BooleanParam`, defines `NAME = "createparent"` and default `true`, and supports Boolean/String constructors.

## Control Flow

String construction treats null as the default `true`; otherwise it parses through the boolean domain. `getName` returns the query key.

## State And Persistence

Only inherited parsed boolean value exists.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.createNonRecursive` with `false` and symlink/create APIs where parent creation is exposed.

## Risks

Defaulting null to true is operation-sensitive; callers that intend omission vs explicit true need to understand inherited serialization behavior.

## Test Signals

Tests should cover null string, true/false values, invalid values, and create-non-recursive URL behavior.
