<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RMDIR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RMDIR3Request.java

## Purpose

RMDIR request DTO carrying parent directory handle and directory name. The source was read as a complete 53-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RMDIR3Request extends RequestWithHandle`, `public static RMDIR3Request deserialize(XDR xdr) throws IOException`, `public RMDIR3Request(FileHandle handle, String name)`, `public String getName()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle plus XDR string; serialize writes handle and UTF-8 bytes.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local check for dot/dotdot or empty directory semantics.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/RMDIR3Request.java -->
