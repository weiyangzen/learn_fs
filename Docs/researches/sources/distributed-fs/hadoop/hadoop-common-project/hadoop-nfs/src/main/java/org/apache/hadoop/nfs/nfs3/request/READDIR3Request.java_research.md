<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIR3Request.java

## Purpose

READDIR request DTO for listing directory entries. The source was read as a complete 68-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READDIR3Request extends RequestWithHandle`, `public static READDIR3Request deserialize(XDR xdr) throws IOException`, `public READDIR3Request(FileHandle handle, long cookie, long cookieVerf,`, `public long getCookie()`, `public long getCookieVerf()`, `public long getCount()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, cookie, cookie verifier, and count; serialize writes them in that order.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

Cookie validity and count limits are deferred to server logic.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READDIR3Request.java -->
