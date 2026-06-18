<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/WRITE3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/WRITE3Request.java

## Purpose

WRITE request DTO carrying file handle, offset, count, stable-how policy, and payload ByteBuffer. The source was read as a complete 93-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class WRITE3Request extends RequestWithHandle`, `public static WRITE3Request deserialize(XDR xdr) throws IOException`, `public WRITE3Request(FileHandle handle, final long offset, final int count,`, `public long getOffset()`, `public void setOffset(long offset)`, `public int getCount()`, `public void setCount(int count)`, `public WriteStableHow getStableHow()`, `public ByteBuffer getData()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, offset, count, stableHow enum value, then opaque byte payload length; serialize writes count twice per NFS WRITE args and writes data.array().

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `ByteBuffer`, `FileHandle`, `WriteStableHow`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Assumes ByteBuffer has an accessible backing array and that count matches payload length; invalid stableHow values may map to null/throw depending enum helper.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/WRITE3Request.java -->
