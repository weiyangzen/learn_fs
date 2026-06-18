<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READLINK3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READLINK3Request.java

## Purpose

READLINK request DTO containing only the symlink handle. The source was read as a complete 43-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class READLINK3Request extends RequestWithHandle`, `public static READLINK3Request deserialize(XDR xdr) throws IOException`, `public READLINK3Request(FileHandle handle)`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads one FileHandle; serialize writes it unchanged.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

The server must later reject non-symlink handles; this class does not type-check.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/READLINK3Request.java -->
