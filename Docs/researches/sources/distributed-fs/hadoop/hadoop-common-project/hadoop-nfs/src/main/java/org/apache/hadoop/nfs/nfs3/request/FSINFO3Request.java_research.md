<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSINFO3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSINFO3Request.java

## Purpose

FSINFO request DTO containing only the queried filesystem handle. The source was read as a complete 42-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class FSINFO3Request extends RequestWithHandle`, `public static FSINFO3Request deserialize(XDR xdr) throws IOException`, `public FSINFO3Request(FileHandle handle)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads one FileHandle; serialize writes it unchanged.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local validation of whether the handle is a filesystem root or file.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/FSINFO3Request.java -->
