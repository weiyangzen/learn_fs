<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READ3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READ3Request.java

## Purpose

READ request DTO for a byte range. The source was read as a complete 62-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READ3Request extends RequestWithHandle`, `public static READ3Request deserialize(XDR xdr) throws IOException`, `public READ3Request(FileHandle handle, long offset, int count)`, `public long getOffset()`, `public int getCount()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, 64-bit offset, and 32-bit count; serialize writes the same.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`, `VisibleForTesting`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Request limits and negative values are not enforced here, so server handlers must bound counts.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READ3Request.java -->
