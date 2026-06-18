# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/ECPolicyParam.java

## Purpose

`ECPolicyParam` carries the WebHDFS `ecpolicy` string parameter for erasure-coding policy operations.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "ecpolicy"` and empty default, and has a string constructor plus `getName`.

## Control Flow

Null or empty-default values are stored as null; non-empty policy names are passed through.

## State And Persistence

Only inherited string value exists.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.enableECPolicy`, `disableECPolicy`, and `setErasureCodingPolicy`.

## Risks

Policy-name validity is deferred to the server. Empty policy may be meaningful for unset operations, so callers must use the right operation/param combination.

## Test Signals

Tests should cover common policy names, empty/null handling, URL encoding, and server rejection of invalid names.
