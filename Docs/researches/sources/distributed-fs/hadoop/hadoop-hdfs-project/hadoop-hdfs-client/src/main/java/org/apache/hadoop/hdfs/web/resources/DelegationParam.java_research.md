# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DelegationParam.java

## Purpose

`DelegationParam` carries an encoded delegation token in the WebHDFS `delegation` query parameter.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "delegation"` and empty default, and has a string constructor plus `getName`.

## Control Flow

Null or empty-default strings become null, suppressing a parameter value through normal `Param` behavior. Non-empty strings are preserved.

## State And Persistence

Only the token string is stored in memory.

## Dependencies And Integration Points

`WebHdfsFileSystem.getAuthParameters` adds it when a delegation token is available.

## Risks

Tokens in URLs can be logged by clients, proxies, or servers. Empty strings are silently omitted.

## Test Signals

Tests should cover URL encoding of token strings, omission for null/empty, and secure-operation auth parameter selection.
