<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RequestWithHandle.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RequestWithHandle.java

## Purpose

Abstract base for requests whose first/primary argument is a FileHandle. The source was read as a complete 35-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public abstract class RequestWithHandle extends NFS3Request`, `public FileHandle getHandle()`.

## Control Flow

Stores a protected final handle and exposes getHandle; subclasses call super(handle) and serialize the handle in their operation-specific order.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `FileHandle`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Constructor is package-private and does not null-check handle; null handles fail later during serialization.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RequestWithHandle.java -->
