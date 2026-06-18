<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKDIR3Request.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKDIR3Request.java

## Purpose

MKDIR request DTO carrying parent directory handle, new name, and settable attributes. The source was read as a complete 62-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class MKDIR3Request extends RequestWithHandle`, `public static MKDIR3Request deserialize(XDR xdr) throws IOException`, `public MKDIR3Request(FileHandle handle, String name, SetAttr3 objAttr)`, `public String getName()`, `public SetAttr3 getObjAttr()`, `public void serialize(XDR xdr)`.

## Control Flow

deserialize reads handle, name, and SetAttr3; serialize writes handle, UTF-8 name, and attributes.

## State and Persistence Behavior

Instances are in-memory RPC argument holders. They persist only for the lifetime of one decoded/constructed NFSv3 call and delegate durable effects to server handlers and the backing filesystem.

## Dependencies and Integration Points

Direct dependencies include `IOException`, `StandardCharsets`, `FileHandle`, `XDR`. Integration points are `XDR` wire encoding, `FileHandle` identity, and the NFSv3 server dispatch layer.

## Risks and Edge Cases

No local validation of empty names, slash characters, or attribute consistency.

## Test Signals

Useful tests are XDR deserialize/serialize round-trips, malformed handle checks, UTF-8 filename cases, negative/oversized count cases, and server-handler integration tests for status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/request/MKDIR3Request.java -->
