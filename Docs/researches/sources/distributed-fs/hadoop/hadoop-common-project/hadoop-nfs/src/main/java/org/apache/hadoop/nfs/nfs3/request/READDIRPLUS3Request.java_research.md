<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIRPLUS3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIRPLUS3Request.java

## Purpose

READDIRPLUS request DTO for entries plus attributes/handles. The source was read as a complete 77-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READDIRPLUS3Request extends RequestWithHandle`, `public static READDIRPLUS3Request deserialize(XDR xdr) throws IOException`, `public READDIRPLUS3Request(FileHandle handle, long cookie, long cookieVerf,`, `public long getCookie()`, `public long getCookieVerf()`, `public int getDirCount()`, `public int getMaxCount()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, cookie, cookie verifier, dirCount, and maxCount; serialize mirrors them.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

dirCount/maxCount bounds and stale cookies are not checked locally.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIRPLUS3Request.java -->
