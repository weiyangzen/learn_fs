<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SETATTR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SETATTR3Request.java

## Purpose

SETATTR request DTO carrying target handle, SetAttr3, and optional ctime guard. The source was read as a complete 85-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class SETATTR3Request extends RequestWithHandle`, `public static SETATTR3Request deserialize(XDR xdr) throws IOException`, `public SETATTR3Request(FileHandle handle, SetAttr3 attr, boolean check,`, `public SetAttr3 getAttr()`, `public boolean isCheck()`, `public NfsTime getCtime()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, SetAttr3, guard boolean, and ctime when guarded; serialize mirrors it.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `NfsTime`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

If check=true with null ctime, serialize will fail; guard mismatch handling lives in server code.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/SETATTR3Request.java -->
