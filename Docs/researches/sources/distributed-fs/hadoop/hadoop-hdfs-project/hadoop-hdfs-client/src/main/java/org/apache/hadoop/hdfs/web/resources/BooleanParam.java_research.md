# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BooleanParam.java

## Purpose

`BooleanParam` is the package-private base for WebHDFS boolean query parameters.

## Important APIs, Types, And Functions

It extends `Param<Boolean, BooleanParam.Domain>`, defines string constants `TRUE` and `FALSE`, overrides `getValueString`, and defines nested `Domain` parser.

## Control Flow

The domain parser accepts case-insensitive `true` or `false` and rejects any other string. Value serialization calls `Boolean.toString`.

## State And Persistence

Only inherited parameter value/domain state exists.

## Dependencies And Integration Points

Subclasses include `AllUsersParam`, `CreateParentParam`, and other WebHDFS boolean params outside this subset.

## Risks

`getValueString` assumes `value` is non-null; callers must avoid serializing null-valued boolean params unless `Param` filters them first.

## Test Signals

Tests should cover case-insensitive parsing, invalid parse errors, null handling through `Param`, and subclass serialization.
