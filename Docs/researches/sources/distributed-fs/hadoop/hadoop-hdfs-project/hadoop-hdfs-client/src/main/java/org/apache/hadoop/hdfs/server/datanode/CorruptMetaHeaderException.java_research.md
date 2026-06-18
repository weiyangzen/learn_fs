# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/CorruptMetaHeaderException.java

## Purpose

`CorruptMetaHeaderException.java` is the package-local exception used when a DataNode block metadata file header is corrupt or truncated.

## Important APIs, Types, and Functions

The class extends `IOException` and provides package-private constructors for message-only and message-plus-cause creation.

## Control Flow

There is no internal flow. `BlockMetadataHeader` throws it from header parsing paths.

## State and Persistence Behavior

It carries standard exception message and cause state. No custom persistence behavior exists.

## Dependencies and Integration Points

The only dependency is `IOException`. It integrates directly with `BlockMetadataHeader` and indirectly with block metadata read paths that need to distinguish corrupt metadata headers from other IO failures.

## Risks and Edge Cases

Constructors are package-private, limiting creation to the datanode package. Callers outside the package can catch it only if they import the public class. No `serialVersionUID` is declared, which can matter for Java serialization warnings but is usually irrelevant for local IO exceptions.

## Test Signals

Tests are mostly through `BlockMetadataHeader`: truncated header and invalid checksum bytes should throw this type and preserve the underlying cause where supplied.
